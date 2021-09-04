import io
import os
import time
import boto3
import shutil
import zipfile
import requests
import calendar
from bs4 import BeautifulSoup
# from flask_restful import Api
from flask import Flask, request


current_timestamp = calendar.timegm(time.gmtime())

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def success_response(data=None, message=None):
    return {
        "data": data,
        "is_success": True,
        "message": message
    }


def error_response(message=None):
    if not message:
        message = "something is wrong"
    return {
        "is_success": False,
        "message": message
    }


def create_folder(folder_name, parent_folder=None):
    directory = folder_name
    parent_dir = "C:/Users/ilikewebsite1"
    if parent_folder:
        parent_dir = parent_dir + f"/{parent_folder}"
    else:
        parent_dir = parent_dir
    path = os.path.join(parent_dir, directory)
    is_dir = os.path.isdir(path)
    if not is_dir:
        os.mkdir(path)
    print(f"Directory '{directory}' created")
    return path


def unzip_folder(folder_path, zip_url):
    zf = zipfile.ZipFile(zip_url, 'r')
    zf.extractall(folder_path)
    zf.close()


def create_zip_dir(dir_path, zip_path):
    zipf = zipfile.ZipFile(zip_path, 'w')
    len_dir_path = len(dir_path)
    for root, _, files in os.walk(dir_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            zipf.write(file_path, file_path[len_dir_path:])
    print(f"Zip '{zip_path}' created")
    return zip_path


def download_zip(url, save_path):
    r = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(save_path)
    print("Zip downloaded and extractall in our folder")


def delete_folder(folder_path, folder_name):
    shutil.rmtree(folder_path)
    print(f"Directory '{folder_name}' deleted")


def generate_s3_link(s3_config, zip_name):
    access_id = s3_config.get("access_id", None)
    access_key = s3_config.get("access_key", None)
    bucket_name = s3_config.get("bucket_name", None)
    s3_zip_name = f"s3_zip_{current_timestamp}"
    region = s3_config.get("region", None)
    content_type = s3_config.get("content_type", None)
    access = s3_config.get("access", None)

    s3_resource = boto3.resource('s3', aws_access_key_id=access_id, aws_secret_access_key=access_key,
                                 region_name=region)

    # Generate aws s3 url for zip
    s3_resource.meta.client.upload_file(
        zip_name,
        bucket_name,
        s3_zip_name,
        ExtraArgs={'ACL': access, 'ContentType': content_type}
    )
    s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_zip_name}"
    return s3_url


def delete_zip(zip_path, zip_name):
    os.remove(zip_path)
    print(f"Deleted '{zip_name}' directory")


# @app.route('/', methods=['POST'])
def generate_project():
    request_data = request.get_json(force=True)

    ZIP_NAME = f"ZIP_{current_timestamp}.zip"

    if request_data:
        json_data = request_data.get("json_data", None)
        folder_name = request_data.get("folder_name", None)
        zip_url = request_data.get("zip_url", None)
        s3_config = request_data.get("s3_config", {})

        if not folder_name:
            folder_name = f"FOLD_{current_timestamp}"

        folder_path = create_folder(folder_name)

        # Download zip folder using request url
        if zip_url:
            download_zip(zip_url, folder_path)

        # Generate folder using request data
        if json_data:
            for key in json_data.keys():
                if isinstance(json_data[key], list):
                    path_sub_folder = create_folder(key, folder_name)
                    for dict_ in json_data[key]:
                        for key_, value in dict_.items():
                            html_code_format = BeautifulSoup(value, 'html.parser').prettify()
                            file = open(f"{path_sub_folder}/{key_}.html", "w")
                            file.write(html_code_format)
                            file.close()

                else:
                    html_code_format = BeautifulSoup(json_data[key], 'html.parser').prettify()
                    file = open(f"{folder_path}/{key}.html", "w")
                    file.write(html_code_format)
                    file.close()

            # Create zip directory for folder
            zip_path = create_zip_dir(folder_path, ZIP_NAME)
            full_zip_path = os.path.join(ROOT_DIR, zip_path)

            # Delete folder
            delete_folder(folder_path, folder_name)

            # Delete zip
            delete_zip(full_zip_path, ZIP_NAME)

            if s3_config:
                url = generate_s3_link(s3_config, ZIP_NAME)
            else:
                url = zip_path

            response_data = success_response(data=url, message="url created successfully")
        else:
            response_data = error_response(message="Didn't get html data")
    else:
        response_data = error_response(message="Didn't get any data")

    return response_data
