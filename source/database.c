
#include <sqlite3.h>
#include <stdio.h>
#include "opendroneid.h"

sqlite3 *db;

void init_db() {
    if (sqlite3_open("../data/data.db", &db)) {
        fprintf(stderr, "Error opening DB: %s\n", sqlite3_errmsg(db));
        return;
    }
    const char *sql = "CREATE TABLE IF NOT EXISTS DroneData("
                      "ID INTEGER PRIMARY KEY, "
                      "Latitude REAL, Longitude REAL, Altitude REAL);";
    sqlite3_exec(db, sql, NULL, NULL, NULL);
}

void insert_data(ODID_UAS_Data *data) {
    char *errMsg = NULL;
    char sql[256];
    snprintf(sql, sizeof(sql),
            "INSERT INTO DroneData (Latitude, Longitude, Altitude) "
            "VALUES (%f, %f, %f);",
            data->Location.Latitude,
            data->Location.Longitude,
            data->Location.AltitudeGeo
            );
    if (sqlite3_exec(db, sql, NULL, NULL, &errMsg)) {
        fprintf(stderr, "Error inserting data: %s\n", errMsg);
        sqlite3_free(errMsg);
    }
}