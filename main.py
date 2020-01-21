import os
import warnings
import pysftp
import sftp_config
from datetime import datetime
from shutil import copyfile

warnings.simplefilter("ignore", UserWarning)

current_date = datetime.now().strftime("%d-%m-%y_%H-%M-%S")


def list_local_files():
    print("Local files:")
    list_local_files.local_files = os.listdir()
    for counter, file in enumerate(list_local_files.local_files):
        print(f"[{counter}] - {file}")


def list_server_files():
    print("Files on server:")
    list_server_files.server_files = sftp.listdir()
    for counter, file in enumerate(list_server_files.server_files):
        print(f"[{counter}] - {file}")


def upload():
    list_local_files()
    print("Please choose a file to upload. Type '0', '1', '2', etc. ")
    while True:
        try:
            file_upload_input = int(input())
            upload.file_upload = list_local_files.local_files[file_upload_input]
            if file_upload_input < 0:
                print("Please choose a valid number within range.")
                continue
            print(f"You have chosen to upload: {upload.file_upload}")
            break
        except IndexError:
            print("Please choose a valid number within range.")
            continue
        except ValueError:
            print("Please type a number, not a string.")
            continue
    sftp_upload()
    print("Job completed.")


def download():
    list_server_files()
    print(f"Current local directory: {os.getcwd()}")
    print("Please choose a file to download. Type '0', '1', '2', etc. ")
    while True:
        try:
            file_download_input = int(input())
            download.file_download = list_server_files.server_files[file_download_input]
            if file_download_input < 0:
                print("Please choose a valid number within range.")
                continue
            print(f"You have chosen to download: {download.file_download}")
            break
        except IndexError:
            print("Please choose a valid number within range.")
            continue
        except ValueError:
            print("Please type a number, not a string.")
            continue
    sftp_download()
    print("Job completed.")


def sftp_upload():
    if sftp.isfile(upload.file_upload) is True:
        while True:
            file_overwrite = input(f"{upload.file_upload} exists already on the server. Would you like to overwrite the file? (yes/no) ")
            if file_overwrite.lower() == "yes":
                sftp.put(upload.file_upload)
                print(f"Uploaded and replaced file: {upload.file_upload}")
                break
            elif file_overwrite.lower() == "no":
                renamed_copy = upload.file_upload[:-4] + "_" + current_date + ".txt"
                copyfile(upload.file_upload, os.getcwd() + "/" + renamed_copy)
                print("Added timestamp to filename.")
                sftp.put(renamed_copy)
                print(f"Uploaded file: {renamed_copy}")
                break
            else:
                print("Please enter 'yes' or 'no'. ")
                continue
    else:
        sftp.put(upload.file_upload)
        print(f"Uploaded file: {upload.file_upload}")
    list_server_files()


def sftp_download():
    if os.path.isfile(download.file_download) is True:
        while True:
            file_overwrite = input(f"{download.file_download} exists already in current working directory. Would you like to overwrite the file? (yes/no) ")
            if file_overwrite.lower() == "yes":
                sftp.get(download.file_download)
                print(f"Downloaded and replaced file: {download.file_download}")
                break
            elif file_overwrite.lower() == "no":
                renamed_file = download.file_download[:-4] + "_" + current_date + ".txt"
                sftp.get(download.file_download, renamed_file)
                print(f"Added timestamp to filename. Downloaded file as: {renamed_file}")
                break
            else:
                print("Please enter 'yes' or 'no'. ")
                continue
    else:
        sftp.get(download.file_download)
        print(f"Downloaded file: {download.file_download}")
    list_local_files()


def select_mode():
    mode = ""
    while mode.lower() not in ("up", "down", "exit"):
        mode = input("Would you like to upload or download files? \nType 'up', 'down' or 'exit': ")
        if mode == "up":
            upload()
            select_mode()
        if mode == "down":
            download()
            select_mode()
        if mode == "exit":
            input("Connection closed. Press enter to exit session.")
            break


# Ignore hostkeys
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

# Initiate SFTP connection
with pysftp.Connection(sftp_config.dnshost, username=sftp_config.username, password=sftp_config.password, port=sftp_config.port, cnopts=cnopts) as sftp:
    with sftp.cd("clients"):
        print(f"Connection to {sftp_config.dnshost}:{sftp_config.port} established. Directory: {sftp.getcwd()}")
        select_mode()
