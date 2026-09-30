# AR Social Media Project

**Location-based augmented reality in the browser, built with Django and AR.js.**

This repo is an extract from an augmented reality socialmedia project, which aims to let people leave digital content (text on virtual signs, images) at real-world coordinates, and lets other people find it by walking past with a phone. There is no app to install and no AR tooling to learn: content is created through an ordinary Django web app, and discovered through a mobile browser.

> **About this repository.** This is code extracted from a larger work-in-progress project. It is a set of Django apps meant to be read, or dropped into a host project and adapted, and not a runnable site. There is no `settings.py`, root `urls.py`, `manage.py` or custom user model here (see [Integrating](#integrating-into-a-host-project) for what the host provides). A [case study PDF](AR%20Project%20Case%20Study.pdf) covers the product thinking.

**Create → Place → Discover → Experience**

---

## The engineering problem

The interesting part isn't putting a 3D object on a camera feed. It's that a location-based platform has to combine things that don't usually meet:

- **Geospatial queries**: return only the content near a user, not the whole database.
- **Untrusted location**: the browser reports where it is, and the server can't take that on faith.
- **Physical-world safety**: content can send people to places. Roads, rail lines, private property and construction sites shouldn't be valid places to leave a message.
- **User-generated content**: everything a normal social platform has to moderate, plus *where* it was placed.

The project is mostly about how those concerns are kept separate, and where they meet.

---

## What's implemented

| App | Responsibility |
| --- | --- |
| `objects` | `ARTextObject` and `ARImageObject` models with geometry, material and interaction settings; reusable object templates; create/edit/delete/like/hide views; automatic moderation on save |
| `channels` | Themed collections of objects (public, verified, seasonal, private) with optional start/end dates; per-creator approval to post text, image or audio; the location-discovery endpoint |
| `moderation` | `RestrictedArea` polygons; user reports; moderator actions (no action, warn, remove content, temporary ban) with email notifications |
| `social` | Friend requests, friendships with independent per-side status, blocking |
| `notifications` | In-app notifications, with optional email |

Objects carry a visibility state (`Public`, `Draft`, `Private`, `Suspended`), and moderation moves content between states rather than deleting it.

---

## How discovery works

```text
Browser geolocation
        │  GET /api/channels/objects/?latitude=…&longitude=…
        ▼
Login required, coordinates parsed as floats (400 on failure)
        ▼
Bounding box of ±50 m around the user   ← cheap, uses the (lat, lon) index
        ▼
Haversine distance filter (≤ 50 m)      ← exact, on the few candidates
        ▼
Return only the fields the AR client needs, bump view counts
        ▼
AR.js / A-Frame creates entities at their GPS positions
```

Two decisions here are worth explaining:

- **Bounding box first, then Haversine.** A raw distance calculation over every row doesn't scale, and a box query can use the composite `(latitude, longitude)` index. The box is computed in metres and converted to degrees, with longitude degrees scaled by `cos(latitude)` because they shrink toward the poles. The box over-selects slightly (its corners are further than 50 m), so Haversine then trims the candidates exactly.
- **A minimal payload.** The endpoint uses `.only(...)` and returns just what's needed to render: text, shape, dimensions, rotation and coordinates. The client never sees the wider data model.

View counts are incremented with a single `F("view_count") + 1` bulk update, which avoids read-modify-write races between simultaneous viewers.

---

## Restricted areas

Users can place content anywhere, and not everywhere should allow it. A `RestrictedArea` is a named polygon (a JSON list of `[lat, lon]` points) with a type (`safety`, `privacy`, `legal`, `sensitive`) and an `active` flag, so moderators can define irregular shapes such as a rail corridor or a school grounds and not just rectangles.

`contains_point()` implements the **ray-casting** point-in-polygon test: cast a ray from the point, count boundary crossings, and an odd count means inside. It uses plain coordinate arithmetic, which is accurate enough for boundaries a few hundred metres across.

On every create or edit, `ARTextObject.moderate_text()` checks the object's coordinates against all active areas. **A match doesn't reject the save.** The object is set to `Suspended`, the reason is recorded in `system_notes`, and the creator gets a notification explaining why. This is a deliberate split between:

- **Geospatial enforcement**: automatic, based on where the content is.
- **Content moderation**: human judgement about what the content means, via reports and moderator actions.

Suspending rather than refusing means creators can see and fix the problem and don't just lose their work. The same pass runs text through a word filter.

---

## Design principles

- **The server decides.** Ownership checks (edit and delete are creator-only) happen server-side, and the client never decides where content may exist.
- **The AR layer only renders.** Business rules stay in Django, and the browser gets pre-filtered, render-ready data.
- **Location is a first-class concern.** It affects discovery, moderation, safety and privacy, and isn't just a pair of columns.
- **Moderation is reversible.** Content moves between visibility states, and the reason is written to an audit trail (`system_notes`) on the object.

---

## Privacy and safety considerations

Precise coordinates can reveal homes, workplaces and routines, and content can influence where people physically go. The design responds with:

- server-side ownership checks on object edit, delete and detail views;
- restricted areas for locations where content shouldn't be placed;
- reporting, blocking, and moderator actions up to temporary bans;
- a word filter on titles, descriptions and content;
- a discovery radius small enough (50 m) that the endpoint never returns a wide area of the map.

The [Known limitations](#known-limitations) section lists where this is still unfinished. Some of it matters for a real deployment.

---

## Integrating into a host project

The apps assume the host provides:

- **Settings and URLs**: `INSTALLED_APPS` for the five apps, the URL includes, `SITE_NAME`, `SITE_DOMAIN`, `DEFAULT_FROM_EMAIL` and email configuration.
- **A custom user model** at `apps.users.CustomUser` (referenced by the channels app) with `user_type` (`'Admin'` / `'User'`), `friends`, `receive_email_notifications`, `account_status` and `ban_expiration`.
- **PostgreSQL**: the models use `ArrayField` (tags, system notes).
- **Python dependencies**: Django, `wordfilter`, and a Postgres driver.
- **Front end**: the AR viewer template loads A-Frame 1.5.0 and AR.js (location-based `gps-camera` / `gps-entity-place`) from CDNs. A-Frame and LocAR builds are also vendored under `static/js/`.

Moderator roles are checked with `user_type` in views, so hosts with their own permission model will want to swap those checks for theirs.

---

## Known limitations

This is extracted work in progress, and these are the gaps I know about. Roughly in order of importance:

1. **Discovery doesn't filter by visibility.** `get_channel_objects` selects by location only, so `Draft`, `Private` and `Suspended` objects can be returned to any logged-in user within range. It should filter to `Public` (and friends' content for friends). `get_friends_objects` returns all of a friend's objects regardless of visibility or location.
2. **The viewer sends fixed test coordinates.** `fetchARObjects` in `channel-viewer-ar.html` uses hard-coded latitude/longitude from development and ignores the device's real position. It needs to pass the `lat` and `lon` it already receives.
3. **Coordinates are only checked for being parseable.** There's no range validation (±90 / ±180), and the server can't verify that a client is actually where it says it is. Spoofed location remains possible.
4. **Debug logging includes usernames and coordinates.** Discovery uses `print` statements, which is at odds with the privacy goals above.
5. **Moderator "remove" doesn't hide content.** `remove_object` sets `is_active = False`, but `ARTextObject` has no such field. It should set `visibility = 'Suspended'`. The email built in `moderate_text` for the creator is also constructed but never sent.
6. **The edit view is wired incorrectly.** It calls `form.save_and_moderate()` (defined on the model, not the form) and redirects to a URL name that doesn't exist.
7. **Uploads aren't implemented in this extract.** The models have no file fields, so upload validation (size and type limits) is still to do. Image and 3D content use texture URLs and templates for now. 3D model support is stubbed out in comments.
8. **The restricted-area check is a simple scan.** Every save tests every active polygon. That's fine at small scale, and the natural next step is PostGIS with a spatial index (which would also replace the bounding box and Haversine code).
9. **There are no automated tests yet** for the geospatial code. Ray casting and the bounding-box maths are the first candidates.

---

## Technology

| Layer | Technology |
| --- | --- |
| Backend | Python, Django |
| Database | PostgreSQL (`ArrayField`, composite index on latitude/longitude) |
| Front end | HTML, JavaScript, Django templates |
| AR | AR.js location-based tracking on A-Frame 1.5.0 |
| Location | Browser Geolocation API |
| Spatial logic | Bounding-box prefilter, Haversine distance, ray-casting point-in-polygon |
| Moderation | `wordfilter`, user reports, restricted areas, moderator actions |

---

## What this project demonstrates

Working across boundaries: authentication, user-generated content, spatial queries, safety policy and a browser-based AR client all have to agree with each other. The focus is on keeping those responsibilities separate (server-side authority, a thin AR client, moderation kept distinct from geospatial enforcement) and on being clear about which parts are finished and which aren't.