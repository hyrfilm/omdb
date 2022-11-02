## omdb:

This project implements a basic movie database in python.
When started it is seeded by 100 movies from OMDB that contains "dude" in the title.
The code is mainly written to be easy to test, maintainable and easy to understand, it's not "production code".

There's a couple of noteworthy trade-offs made though:
1. There's no mocking in the unit-tests
2. Most of the efforts (in terms of testing) have been done towards API/integration tests.

Regarding, 1: I generally consider mocking to be a necessary evil at best and a anti-pattern at worst.
This is because it tends to break encapsulation, irrelevant changes often breaks tests and when there's a lot
of mocking going on there's even a question of what value the test serves. Integrating with external systems are
of course often necessary but in those cases I tend to prefer stubbing. In this case, though, I simply chose to
do neither and simply let the tests call the "real" interfaces. In a "real world" scenario this might be a bad idea
although I think it's always good to base those decisions on emperical data :)

Regarding 2, this project has more integration test/API-tests than unit-tests. This is done by using a tool called
skivvy (created by yours truly) that can be found here: github.com/hyrfilm/skivvy
There's several reasons why I chose to go down this route, testing the API-directly means that nothing needs to be
"simulated" / "mocked" which increases the chances of the tests actually finding errors. The other reason I chose
to do this is because it's possible to test the "whole chain" (similar to e2e-tests) including things like OAuth
authenticaion etc which could otherwise be a bit messy to test. The third reason is that creating the API-tests
are quite a low-cost in terms of effort. The main idea behind skivvy tests is that the tests are of the same
kind as what you're testing (json over http), you also only provide what you're interested in testing (unlike
snapshots) which means that it's possible to have simple focused API-tests that don't break because an irrelevant
change was done.
The skivvy tests can be found under `api_tests`. You can read more about skivvy here: github.com/hyrfilm/skivvy
(For simplicity these tests are run in a docker container, so nothing needs to be installed via pip)

start the backend:
	gunicorn backend.gunicorn:application

run unit-tests tests:
	python test.py

run api-tests / integration tests (mac):
	cd api_tests && source skivvy_mac.sh

run api-tests / integration tests (linux):
	cd api_tests && source skivvy_linux.sh
