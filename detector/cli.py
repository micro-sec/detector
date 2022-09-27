import json
import traceback

import click
import requests
from jsonschema import validate

from detector.config import *
from detector.utils import schema_monitoring, schema_inspecting


@click.group()
def cli():
    """A CLI for intrusion detection on microservices applications."""
    pass


@cli.command()
def status():
    """Check the status of the daemon"""
    try:
        response = requests.get("http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/daemon/status")
        if response.status_code == 200:
            if response.content.decode() == "null\n":
                click.echo("The Daemon is running but no configuration was provided.")
            else:
                click.echo("The Daemon is running. The current configuration is the following:")
                click.echo(response.content.decode())
    except Exception:
        click.echo("The Daemon is currently not running.")
        traceback.print_exc()


@click.option("-f", "--filename", help="Filename that contains the configuration to apply.")
@cli.command()
def start(filename):
    """Start collecting system calls on all nodes by specifying a JSON file."""
    # Get and validate data from JSON
    try:
        with open(r"" + filename) as file:
            data = json.load(file)
            validate(instance=data, schema=schema_monitoring)
    except Exception:
        traceback.print_exc()
        click.echo("Please specify a valid JSON file using the flag \"-f\" or \"--filename\"")
        return

    response = requests.post("http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/monitoring/start", json=data)
    click.echo(response.content.decode())


@cli.command()
def stop():
    """Stop collecting system calls on all nodes."""
    response = requests.post("http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/monitoring/stop")
    click.echo(response.content.decode())


@click.option("-f", "--filename", help="Filename that contains the configuration to apply.")
@cli.command()
def inspect(filename):
    """Start inspecting the system calls by specifying a JSON file."""
    # Get and validate data from JSON
    try:
        with open(r"" + filename) as file:
            data = json.load(file)
            validate(instance=data, schema=schema_inspecting)
    except Exception:
        traceback.print_exc()
        click.echo("Please specify a valid JSON file using the flag \"-f\" or \"--filename\"")
        return

    response = requests.post("http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/inspecting/start", json=data)
    click.echo(response.content.decode())


@click.option("-n", "--size", default=5, help="Show 'n' latest alarms")
@click.option("--delete", is_flag=True, help="Delete alarms.")
@cli.command()
def alarms(size, delete):
    """List alarms detected."""
    if delete:
        requests.delete("http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/alarms")
        click.echo("Alarms were successfully deleted.")
    else:
        if size:
            try:
                size = abs(int(size))
                response = requests.get("http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/alarms?size=" + str(size))
            except ValueError:
                response = requests.get("http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/alarms")
        else:
            response = requests.get("http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/alarms")
        click.echo(response.content.decode())


@cli.command()
def algorithms():
    """List all the algorithms available."""
    response = requests.get("http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/algorithms")
    click.echo(response.content.decode())


@click.option("--pods", is_flag=True, help="List pods.")
@click.option("--services", is_flag=True, help="List services.")
@click.option("--deployments", is_flag=True, help="List deployments.")
@click.option("--namespaces", is_flag=True, help="List namespaces.")
@click.option("--nodes", is_flag=True, help="List nodes.")
@click.option("-a", "--all", is_flag=True, help="List all resources.")
@click.option("-n", "--namespace", default="default",
              help="Specifies a namespace. If no namespace is specified, defaults to \"default\".")
@cli.command()
def list(pods, services, deployments, namespaces, nodes, all, namespace):
    """List resources of the cluster."""
    if pods or services or deployments or namespaces or nodes or namespaces or all:
        if pods or all:
            click.echo("=== PODS ===")
            response = requests.get("http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/resources/pods?namespace=" + namespace)
            for i in response.json():
                click.echo(i["metadata"]["name"])
        if services or all:
            click.echo("=== SERVICES ===")
            response = requests.get("http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/resources/services?namespace=" + namespace)
            for i in response.json():
                click.echo(i["metadata"]["name"])
        if deployments or all:
            click.echo("=== DEPLOYMENTS ===")
            response = requests.get("http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/resources/deployments?namespace=" + namespace)
            for i in response.json():
                click.echo(i["metadata"]["name"])
        if namespaces or all:
            click.echo("=== NAMESPACES ===")
            response = requests.get("http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/resources/namespaces?namespace=" + namespace)
            for i in response.json():
                click.echo(i["metadata"]["name"])
        if nodes or all:
            click.echo("=== NODES ===")
            response = requests.get("http://127.0.0.1:" + str(DETECTOR_PORT) + "/api/resources/nodes?namespace=" + namespace)
            for i in response.json():
                click.echo(i["metadata"]["name"])
    else:
        click.echo("No resource specified. Type --help for more information.")


if __name__ == "__main__":
    try:
        cli()
    except requests.exceptions.ConnectionError:
        click.echo("Please make sure the detector is running")
