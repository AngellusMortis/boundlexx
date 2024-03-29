2021-05-03
----------

* Adds Huey to eventually replace Celery. `boundlexx.notifications` tasks
    migrated. New tasks are (mostly) designed to run _without_ Django or DB.
* Adds `/ingest-*` endpoints under main API with seiralizers and everything
* Adds `/ingest/world-forum-id/` endpoint for Huey

2021-05-01
----------

* Upgrades to Python 3.9
* Upgrades to Django 3.2
* Squashes all existing mirgations
* Updates Azure code to match new Terraformed environment
* Updates static file caching to be smarter

2021-04-25
----------

* Updates `html_name` fields to escape all existing HTML before calculating

2021-04-17
----------

* Removes `BoundlessClient` to seperate private repo
* Migrates Docker Images from `docker.pkg.github.com` to `ghcr.io`
* Removes Google Sheets related tasks/code
* Adds `ModelDiffMixin` to only update World model when it actually changes
* Adds `last_updated` to `/worlds/` and accompanying filter

2021-04-16
----------

* Adds thumbnail images for Worlds, Item and Emojis
* Adds `default_color` for Items and uses it to determine default item image
* Adds `/metals/` endpoint

2021-04-14
----------

* Adds images for items
* Adds item images to forum template
* Updates purge_cache command to purged redis cached data


2021-03-30
----------

* Adds permissions to allow authed users to access private worlds

2021-03-29
----------

* Adds world image creation from Atlas image dumps

2021-03-28
----------

* Removes deprecated listWorld endpoint on v1
* Fixes set of world IDs that get searched for
* Fixes initial resources not being added back to forum post on update

2021-03-27
----------

* Fixes length of guild_tag for longer guild names
* Fixes issue for uploading JSON for perm worlds
* Adds server address to world list view
* Fixes for testing version 249.4

2021-03-21
----------

* Upgrades to docker-compose file 3.8 spec

2020-11-04
----------

* Adds full categorization of Emojis
* Adds update link to forum template generator
* Refactors Boundless Client

2020-11-01
----------

* Adds affiliation attrbution/disclaimer.
* Changes resources to properly pull from game files.
* Adds `prestige`, `mine_xp`, `build_xp`, `is_liquid`, `is_block`, and `resource_data` to `retrieveItem` API.
* Fixes time to generate API Schemas
* Adds beacons endpoint on the Worlds API

2020-10-31
----------

* Adds `atlas_image_url` to `listWorlds`

2020-10-30
----------

* Fixes location seiralizer for Shop API endpoints

2020-10-29
----------

* Adds atlas images for worlds

2020-10-27
----------

* Adjusts default filters for shop API endpoints

2020-10-26
----------

* Adds better handling for permissions on Homeworld/Exoworlds
* Removes Creative Worlds from Resource count endpoints

2020-10-21
----------

* Removes all data from Worlds from v1 and v2 for worlds that are not `is_public`

2020-10-20
----------

* Adds parallelization to Shop Price polling
* Adds `text_name`/`html_name` for Leaderboard and Shop prices

2020-10-19
----------

* Adds missing `count` to Recipe API
* Adds `has_colors` and `is_resource` to Items API
* Adds `is_public`, `is_public_edit`, `is_public_claim` to Worlds list API

2020-10-11
----------

* Adds `world_class` to Worlds API

2020-10-10
----------

* Adds remaining endpoints to v2 API
* Replaces `_average_per_chunk` filter with proper `average_per_chunk` one
* Adds `list_type` to Items list. Also adds filter for it.

2020-10-09
----------

* Adds subtitles to v2 Items list endpoint
* Adds `is_boundless_only` + filter to Emojis

2020-10-08
----------

* Fixes performance issue with deuping search results
* Adds initial pass of v2 endpoints

2020-10-06
----------

* Added `/api/v1/forum/` that mimics the actual forum form one.
* Changes `msgpack` format to follow the same optmization that Boundless uses on their msgpack Serialization

2020-10-04
----------

* Adds alt text/title to emoji images
* Adds searching by ID for Worlds, and GameObjs
* Adds `image_url` to Worlds Simple

2020-10-02
----------

* Fixes operation IDs so they play nicely with `openapi-client-axios` Node.js package

2020-10-01
----------

* Deprecates Worlds List endpoint in favor of the Worlds Simple List endpoint
    * The Simple List endpoint will replace the normal List endpoint around 2020-12-1
* Adds earching to Emojis API
* Changes the logic for "inactive" worlds and world block colors to be more consistent
    * Seralizers for both Worlds and WBC APIs will not return the `active` field
    * `show_inactive` will function on Worlds and WBCs APIs
    * `show_inactive_colors` will function on all WBCs endpoints
    * Adds filters for `active` and `world__active` to the Worlds and WBCs APIs

2020-09-29
----------

* Adds bows to World API
* Adds Recipes and Recipe groups APIs
* Adds Sovereign Blocks endpoint to the Colors API

2020-09-28
----------

* Adds max limit of 1000 items for `limit` filters.
* Changes filter logic to return HTTP 400 for any unknown filters to prevent cache busting

2020-09-26
----------

* Adds a 5 request per second per view rate limit

2020-09-24
----------

* Adds `format=msgpack` format to APIs
* Adds Blocks API
* Adds Dump endpoint to Worlds API
    * Only supports `format=msgpack`
    * Cached heavily for 1 hour
* Adds `html_name` and `text_name` to Worlds API
* Adds `sort_name` ordering filter to the Worlds API
* Adds `is_public_edit` and `is_public_claim` to the Worlds API

2020-09-22
----------

* Adds Sovereign colors endpoint to Items API
* Adds performance improvements for polling worlds to hand the sheer number of new worlds
* Adds WIP endpoint to pull World Control data from Sovereign worlds
* Adds WIP Discord Webhook notification for new colors


2020-09-20
----------

* Changes existing color booleans on WBC APIs to reflect how "new color" logic works with new Sovereign worlds.
* Adds "Forum Template Generator"
* Changes Discord Webhook post format to be more inline with Forum Template
* Adds `average_per_chunk` field to the Resource Counts endpoints

2020-09-16
----------

* Changes default API Schema render from ReDoc to SwaggerUI
* Adds `start_after`, `start_before`, `end_after`, and `end_before` filters to Worlds API
* Changes all time filters to use ISO 8601 timestrings

2020-09-15
----------

* Adds minting values and more locaization/string data to Items API
* Adds atmosphere protection info to the Worlds API
* Adds Skills and Skill Groups APIs
* Adds Emojis API
* Adds Game File API (requires API key auth)

_Note_: Thanks to willcrutchley for the hard work to actually get the images from the game files

2020-09-12
----------

* Changes frontdoor to API to Azure CDN instead of Cloudflare
* Changes `format=json` to the default format instead of `format=api`
* Adds dynamic caching for worlds


2020-09-02
----------

* Adds Shop Prices for Items to the Items and Worlds APIs.
    * Currently only aviable for the Testing Universe instance. Still need API key for Live Universe
* Adds `is_resource` and `has_colors` filters to the Items API
* Adds `show_inactive` filter to Worlds API
* Adds `show_inactrive_colors` filter to the World Block Color APIs
* Changes Colors List endpoint to only return a single result per color

2020-08-28
----------

* Adds image URLs and forum posts URLs to Worlds API
* Adds warp/portal costs details to the World Distances API

2020-08-06
----------

* Adds Timeseries endpoints for World Polls and Item Resource Counts

2020-08-05
----------

* Adds Trigram/Gin index for Postgres to allow for full text/fuzzy search endpoints
* Adds filters to Worlds and Items APIs

2020-08-03
----------

* Adds Webhook notifications for new Exoworlds
* Adds parsing color data from DB Google Sheet

2020-07-31
----------

* Adds `Live Universe instance <https://api.boundlexx.app>`_.
* Adds API endpoint World Block Color data.
* Adds ingestion URL to pull in a "World JSON" file from the game
* Adds Celery task to parse Exoworld data from forums
* Adds RGB Hex values to Colors API
* Adds Cloudflare caching layer


2020-07-28
----------

* Initial release with `Testing Universe version <https://testing.boundlexx.app>`_.
