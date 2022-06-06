# Graphent Opensafely - Release hatch
Release hatch is a REST API application which can be used to expose the output file created by the job-runner. The user can use the https://jobs.opensafely.org to navigate to a web page that contain cross site ajax API to access this application service and display the output on the https://jobs.opensafely.org. So this service should be hosted on a security environment which can only be accessed from a secure network, e.g. via VPN or remote desktop.

In order to expose the output data, the deployment of this application service should be configured to have a local directory which can access the workspace. For K8S instance, this can be done by adding the persistent volume to the deployment.

## development
This application can be tested in a local debug mode by running the [localrun.py](./localrun.py) with the following steps:
1. create `.env` in the project root folder based on the template `dotenv-sample.env`
2. copy the sample `workspaces` folder to the project root folder (one of the workspace is called `test-ws` in the sample)
3. install `just` based on [DEVELOPERS.md](./DEVELOPERS.md)
4. generate the credential by calling the `just` command `just client token -w test-ws -u chirsyeunggraphnet -d 1000000` and copy the `auth-token`
5. run (or run with debug) `localrun.py`
6. open http://lcoalhost:8001/docs in the browser
7. press the `Authorize` button and paste the `auth-token`
8. run the `GET /workspace/testing/current` API to see the result
9. on the job-server side, open the DB and add `http://localhost:8001` to the `jobserver_backend.level4_backend` of the backend want to use this release hatch
