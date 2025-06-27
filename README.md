# Simple IoT Device Status Service

This project acts as a backend to accept IoT status updates via HTTP.
API:
 * `POST` a device status with to `/status`
   * The payload must have the following fields:
   
     | field          | data type | notes                     |
     |----------------|-----------|---------------------------|
     | device_id      | str       |                           |
     | timestamp      | str       | must be valid datetime    |
     | battery_level  | int       | must be in range [0, 100] |
     | rssi           | int       | signal strength           |
     | online         | bool      |                           |
     

 * `GET` the most recent status for a device with at `/status/{device_id}`
 * `GET` the most recent status for all devices at `/status/summary`

Features:
* API key authorization (see [Configuration](#Configuration))

## Installing and running the server

Python 3.12+ and a Unix-based machine is required to install this program.
Older versions of Python3 may work, but it is not guaranteed.

Do `make` to install dependencies and start the server at `localhost:8000`.
This is equivalent to `make install` and then `make run`.

## Configuration

Optionally, you can specify configurable variables. Create a file
`config.ini` with any of the following options:
* In the `general` section:
  * `key` specifies the valid API key. An API key is only enforced if
    one is listed here.
* In the `database` section:
  * `url` specifies the database file url. By default, it is 
    `sqlite:///./iot_test.db`.

## Testing

Do `make test` to run the unit and integration tests.
This command will also install any dependencies needed for testing.

To test with a coverage report, do `make cover`.

## Other useful `make` commands

`make clean` will remove virtual environment and testing artifacts.

`make clean-db` will remove the production database 
(and any testing databases, but those are removed by `make clean` as well).

## Implementation details

#### API interface

The API interface was implemented using the FastAPI library. This enabled quick
development with robust features like payload validation and automatic 
JSON response translation. The API functions are marked async to avoid a 
bottleneck in case the database operations are slow.

On top of FastAPI, the ASGI server Uvicorn is used, which is the standard choice
when using FastAPI.

#### Database

The server utilizes a SQLite backend interfaced through SQL Alchemy.
The database is implemented as a thread-safe singleton object – sessions
are not shared between threads. 

The database code is also used in tests, instead of mocking a database.
This is done safely by setting an environment variable during testing where
certain functions can only be called. Additionally, the database file created 
during testing is separate from the production database.

#### Code extensibility

A reasonable amount of time was spent making the code easily extensible. For 
example, the singleton functionality was abstracted out so that it can be easily 
used by modules other than the database. Likewise, a configuration file is used 
to control other elements (like the database file name). Thus, adding more endpoints 
and functionality should be very simple. 

## CI/CD

# TODO
