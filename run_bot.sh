#!/bin/bash
DB=bot.db

if [[ ! -f "$DB" ]]; then
    touch bot.db
    cat schema.sql | sqlite3 bot.db
    echo "DB CREATED"
else
    echo "DB FOUND"

fi

python bot.py



