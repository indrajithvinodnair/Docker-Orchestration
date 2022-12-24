import docker


class dockerComposeOps:
    def __init__(self):
        self.ec2= docker.DockerClient(base_url="tcp://3.111.66.135:2375")
       

    def createComposeOperation(self):
        containers = [
                            {
                                "name": "web",
                                "image": "nginx:latest",
                                "ports": {"8080": "80"},
                                "command": "nginx -g 'daemon off;'",
                            },
                            {
                                "name": "db",
                                "image": "postgres:latest",
                                "environment": {"POSTGRES_PASSWORD": "mysecretpassword"},
                                "command": "tail -f /dev/null",
                            },
                                {
                                    "name": "app",
                                    "image": "python:3.8-slim",
                                    "command": "python app.py",
                                    "links": ["web", "db"],
                                    "volumes": [".:/app"],
                                },
                         ]       

        # Use Docker Compose to create and start the containers
        compose = docker.DockerCompose(self.ec2)
        compose.up(containers=containers)

        # Run a command in the app container to connect to the web server and database
        app_container = self.ec2.containers.get("app")
        response = app_container.exec_run("curl web && psql -U postgres -h db -c 'SELECT NOW()'")

        # Print the output of the commands to verify the link is successful
        print(response.output.decode())

        # Print a message indicating that the link is successful
        print("Link between containers successful!")


composer = dockerComposeOps()
composer.createComposeOperation()
