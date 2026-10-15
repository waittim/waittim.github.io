#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

const configPath = path.join(__dirname, "..", "_config.yml");
const text = fs.readFileSync(configPath, "utf8");
const re = /^(asset_version:\s*")(\d{8})-(\d{2,})(")[ \t]*$/m;
const match = text.match(re);

if (!match) {
  console.error(
    "Could not find asset_version in YYYYMMDD-NN form in _config.yml"
  );
  process.exit(1);
}

const now = new Date();
const today = [
  now.getFullYear(),
  String(now.getMonth() + 1).padStart(2, "0"),
  String(now.getDate()).padStart(2, "0"),
].join("");
const currentDate = match[2];
const currentSeq = Number(match[3]);
const nextSeq = currentDate === today ? currentSeq + 1 : 1;
const next = `${today}-${String(nextSeq).padStart(2, "0")}`;
const updated = text.replace(re, `$1${next}$4`);

if (updated === text || updated.split("\n").length !== text.split("\n").length) {
  console.error("asset_version was not updated");
  process.exit(1);
}

fs.writeFileSync(configPath, updated);
console.log(`asset_version ${currentDate}-${match[3]} -> ${next}`);
