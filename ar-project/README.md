# Pataverse

**Location-based augmented reality built with Django, AR.js and A-Frame.**

Pataverse is a personal project exploring how browser-based augmented reality can be used to create, place and discover digital content within physical environments.

The platform allows users to create location-based content without requiring specialist AR software, a native mobile application or their own AR development environment. Content can consist of text, images or 3D assets and is associated with a real-world geographic location.

Users can then open the AR experience through a mobile browser and discover digital content positioned around their physical surroundings.

The project combines conventional web application development with **geolocation, augmented reality, user-generated content, access control and location-aware safety mechanisms**.

---

## Concept

Pataverse is built around a simple interaction model:

**Create → Place → Discover → Experience**

### Create

Users create digital content through the conventional Django application.

This can include:

* Text-based messages
* Images
* 3D content
* Location-based experiences

The creation process deliberately hides the underlying AR implementation from the user.

### Place

Each piece of content is associated with a real-world position using latitude and longitude.

This turns a conventional database record into something spatial: the content is not simply stored in the application, but associated with a specific place in the physical world.

### Discover

When a user accesses the AR interface, their current location can be used to identify nearby content.

Rather than downloading the entire collection of artwork, the backend can return only content relevant to the user's current position and discovery radius.

### Experience

The browser uses **AR.js and A-Frame** to render the returned content within the user's physical surroundings.

The result is a system where the physical environment becomes part of the application's interface.

---

# Architecture

```text
┌─────────────────────────────┐
│       Mobile Browser        │
│                             │
│  Camera + Geolocation       │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       AR.js / A-Frame       │
│                             │
│   AR tracking + rendering   │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│      Django Application     │
│                             │
│ Auth · Permissions · Logic  │
│ Content · Moderation        │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│         PostgreSQL          │
│                             │
│ Users · Artwork · Locations │
│ Permissions · Restrictions  │
└─────────────────────────────┘
```

The architecture deliberately separates responsibilities.

**Django** is responsible for application logic, authentication, permissions, content management, and validation, and provides structured data to the browser and controls what content is returned.

**AR.js / A-Frame** handles the client-side AR experience and rendering.

**PostgreSQL** stores users, content, relationships and geographic information.

---

# Geospatial Architecture

Location is a fundamental part of Pataverse rather than simply metadata attached to an artwork.

Artwork is currently represented using latitude and longitude fields:

```python
class Artwork(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
```

When content is requested, the user's location can be passed to the backend and used to determine which content is relevant.

The important architectural principle is that **location received from the client is treated as untrusted input**.

The server remains responsible for deciding whether a location is valid and whether content is allowed to exist there.

---

## Location Discovery

The discovery process can be thought of as:

```text
User's location
      ↓
Validate coordinates
      ↓
Determine discovery radius
      ↓
Find relevant artwork
      ↓
Return structured response
      ↓
Create AR entities
      ↓
Render in browser
```

This avoids sending the complete artwork collection to the client.

It also means that the AR layer does not need to understand the application's complete data model. It receives the content it needs and concentrates on presenting it.

---

# Restricted Areas

One of the interesting consequences of allowing users to place content anywhere is that **not every geographic location should necessarily be available for content placement**.

Pataverse therefore includes the concept of restricted areas.

A restricted area can be represented as a polygon containing a series of latitude/longitude points:

```python
class RestrictedArea(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    boundary = models.JSONField()

    restriction_type = models.CharField(
        max_length=20,
        choices=(
            ("safety", "Safety"),
            ("privacy", "Privacy"),
            ("legal", "Legal"),
            ("sensitive", "Sensitive Location"),
        )
    )

    active = models.BooleanField(default=True)
```

For example:

```json
[
    [52.0001, -1.5002],
    [52.0034, -1.4978],
    [52.0041, -1.4921],
    [52.0017, -1.4895],
    [51.9998, -1.4940]
]
```

This allows restricted areas to have irregular boundaries rather than being limited to simple rectangular boxes.

A point-in-polygon calculation can then determine whether an artwork falls inside one of these areas.

```python
def contains_point(self, latitude, longitude):
    inside = False
    j = len(self.boundary) - 1

    for i in range(len(self.boundary)):
        lat_i, lon_i = self.boundary[i]
        lat_j, lon_j = self.boundary[j]

        if (
            (lat_i > latitude) != (lat_j > latitude)
            and longitude <
            (lon_j - lon_i)
            * (latitude - lat_i)
            / (lat_j - lat_i)
            + lon_i
        ):
            inside = not inside

        j = i

    return inside
```

The artwork placement process can then reject locations that fall inside an active restricted area.

This creates an important distinction between **moderation** and **automated enforcement**.

Moderators or administrators can define and manage restricted areas, but the application automatically enforces those restrictions when content is created or moved.

---

# Interesting Engineering Problems

Pataverse became substantially more interesting once the different systems had to work together.

The individual technologies are relatively straightforward. The difficult part is managing the boundaries between them.

## 1. Geospatial queries

The application needs to determine which content is relevant to a user's physical location.

Artwork is stored with geographic coordinates and the backend can use the user's coordinates and a discovery radius to determine what should be returned.

This creates a direct relationship between:

**physical location → database query → AR scene**

---

## 2. Browser-based AR

Rather than requiring users to install a native application, Pataverse uses browser-based AR.

**AR.js** provides the AR functionality while **A-Frame** provides a declarative framework for constructing and rendering the scene.

This means the browser has to handle:

* Camera access
* Location access
* AR tracking
* Rendering
* User interaction
* Network communication

while also remaining usable on mobile hardware.

The benefit is a significantly lower barrier to entry: the user can access the experience through a browser rather than installing specialist software.

---

## 3. Untrusted location data

A browser can provide coordinates, but the server cannot assume that those coordinates are trustworthy.

A malicious client could submit:

* Invalid latitude values
* Invalid longitude values
* Artificial coordinates
* Coordinates inside a restricted area
* Coordinates intended to manipulate discovery

Consequently, important location decisions happen server-side.

For example:

```text
Client submits coordinates
        ↓
Validate coordinate ranges
        ↓
Check permissions
        ↓
Check restricted areas
        ↓
Save / reject
```

The client therefore cannot simply decide where an artwork is allowed to exist.

---

## 4. Dynamic content discovery

A city could potentially contain a very large number of artworks.

Sending all of them to every user would be inefficient and would make the AR client responsible for filtering content that it does not need.

Instead:

```text
Current user location
        ↓
Geospatial filtering
        ↓
Nearby artwork
        ↓
AR client
```

The backend acts as the first layer of filtering, reducing both network traffic and client-side processing.

---

## 5. User-generated 3D content

Allowing users to upload their own assets creates a different class of problems from ordinary text-based content.

Uploaded files are untrusted and can be:

* Excessively large
* An unsupported format
* Malformed
* Unexpectedly complex
* Unsuitable for client-side rendering

The application therefore needs to validate uploaded content before it reaches the AR layer.

File size restrictions and permitted file types provide an initial control layer, while keeping uploaded content separate from executable application code reduces the risk associated with user-controlled files.

---

## 6. Physical-world constraints

Pataverse differs from a conventional social platform because its content can influence where people physically go.

A poorly designed system could encourage users towards:

* Roads
* Railway infrastructure
* Construction areas
* Private property
* Poorly lit locations
* Other sensitive or hazardous areas

This makes geographic restrictions more than a conventional moderation feature.

The application can use restricted areas and content controls to prevent or limit placement in locations where the digital experience could create physical-world risks.

---

# Security & Privacy

Pataverse handles several categories of potentially sensitive information:

* User accounts
* Precise geographic coordinates
* User-generated content
* Uploaded files
* Relationships between users
* Private/friends-only content

Security therefore has to exist across multiple layers.

### Authentication and authorisation

Django handles authentication and protected functionality.

Ownership and visibility checks are performed server-side rather than trusting the client to decide which content a user can access or modify.

### Input validation

Client-provided data is treated as untrusted.

This applies to:

* Artwork IDs
* Coordinates
* Text
* File uploads
* Geolocation data
* Visibility settings

### Location privacy

Precise geographic information can reveal sensitive places such as homes, workplaces or regularly visited locations.

The architecture therefore favours data minimisation and avoids exposing location information unnecessarily.

### Private content

Pataverse supports public and private/friends-only content.

Private content must be filtered at the application layer so that it cannot simply be discovered by manipulating an HTTP request.

### Upload security

User-provided files are validated for type and size before being stored and exposed to the client.

---

# User-Generated Content

The platform is designed around the idea that users can create the content that populates the physical environment.

That introduces moderation challenges including:

* Offensive content
* Harassment
* Spam
* Copyright infringement
* Inappropriate material
* Defamatory content
* Malicious links
* Abusive placement of content

Potential platform controls include:

* User reporting
* Blocking
* Content removal
* Copyright takedown processes
* Content classification
* Creation limits
* Rate limiting
* URL restrictions
* Administrative moderation

The important distinction is between **content moderation** and **geospatial enforcement**.

Moderation deals with what content means and whether it should remain available.

Geospatial enforcement determines whether content is allowed to exist at a particular location in the first place.

---

# Public Experiences

The location-based model allows Pataverse to support experiences beyond simply leaving messages at random locations.

### Seasonal experiences

Users could create Halloween walks or other seasonal trails, with content appearing at specific locations along a route.

### Historical experiences

Archival photographs, historical information and stories could be positioned alongside the locations they relate to.

### Creative experiences

Artists could create virtual public exhibitions, placing digital sculptures, paintings and installations around a city without requiring a physical gallery.

This demonstrates the broader concept behind Pataverse: **the physical environment can become a canvas for user-generated digital experiences.**

---

# Design Principles

Several principles shaped the implementation.

### Server-side authority

The browser can request an action, but the Django application decides whether that action is permitted.

### Minimal client responsibility

The AR client concentrates on rendering and interaction rather than implementing application security or business rules.

### Location as a first-class concern

Geographic information affects discovery, permissions, safety and the user experience rather than being treated as ordinary metadata.

### Progressive complexity

The underlying system can support sophisticated spatial behaviour without exposing that complexity to users.

### Browser-first accessibility

Users should not need specialist software or a dedicated AR development environment to participate.

---

# Technology

| Layer                | Technology                                        |
| -------------------- | ------------------------------------------------- |
| Backend              | Django / Python                                   |
| Database             | PostgreSQL                                        |
| Frontend             | HTML / JavaScript                                 |
| AR                   | AR.js / A-Frame                                   |
| Location             | Browser Geolocation API                           |
| Content              | User-generated text, images and 3D assets         |
| Spatial restrictions | Coordinate polygons / point-in-polygon validation |

---

# What This Project Demonstrates

Pataverse was primarily an exploration of **systems engineering rather than AR for its own sake**.

The project required several conventional web development concerns to interact with a spatial interface:

```text
Authentication
      +
Permissions
      +
User-generated content
      +
Geolocation
      +
Spatial validation
      +
AR rendering
      +
Privacy & safety
      ↓
Location-based digital experience
```

The interesting engineering problem is therefore not simply:

> "How do I put a 3D object on a camera feed?"

It is:

> **How do I build a system where digital content can safely, securely and meaningfully exist within physical space?**

Pataverse explores that question using a conventional Django architecture combined with browser-based augmented reality.

---

## Project Status

Pataverse is a personal project and an exploration of the architecture and engineering challenges involved in location-based AR.

Some components are experimental or intentionally simplified, particularly the geospatial implementation. A production-scale deployment would likely introduce more sophisticated spatial indexing, asset processing, moderation infrastructure, observability and privacy controls.

The project is therefore best understood as both a working application and an exploration of how a conventional web stack can be extended into a spatial computing environment.

---

## Technology Summary

**Django · Python · Django REST Framework · PostgreSQL · JavaScript · AR.js · A-Frame · Browser Geolocation · User-Generated Content · Geospatial Validation**
