#!/usr/bin/env node

const SteamUser = require("steam-user");

sentry_dir = process.env.STEAM_SENTRY_DIR
steam_username = process.env.STEAM_USERNAME
steam_password = process.env.STEAM_PASSWORD
app_id = Number(process.env.STEAM_APP_ID)

s = new SteamUser({ "dataDirectory": sentry_dir });
s.logOn({ "accountName": steam_username, "password": steam_password, "rememberPassword": true });

callback = function (err, t) {
    if (err) {
        console.error(err);
        process.exit(1);
    }
    else {
        console.log(t.toString("hex"));
        process.exit(0);
    }
}

setTimeout(function () {
    s.getAuthSessionTicket(app_id, callback);
}, 5000);
