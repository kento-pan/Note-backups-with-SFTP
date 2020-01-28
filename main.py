import os
import warnings
import pysftp
import sftp_config
import pyAesCrypt
from paramiko.ssh_exception import SSHException

warnings.simplefilter("ignore", UserWarning)

bufferSize = 64 * 1024
aes_password = "PLACEHOLDER"


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


def encrypt():
    encrypt.file_upload_input = int(input())
    upload.selected_file = list_local_files.local_files[encrypt.file_upload_input]
    upload.encrypted_file = upload.selected_file + ".enc"
    print(f"Encrypting {upload.selected_file}..")
    pyAesCrypt.encryptFile(upload.selected_file, upload.encrypted_file, aes_password, bufferSize)
    print(f"Encrypted as {upload.encrypted_file}")


def decrypt():
    print(f"Decrypting {download.file_download}..")
    pyAesCrypt.decryptFile(download.file_download, download.file_download[:-4], aes_password, bufferSize)
    print(f"Decrypted as {download.file_download[:-4]}")
    os.remove(download.file_download)
    print(f"{download.file_download} deleted from disc.")


def upload():
    list_local_files()
    print("Please choose a file to upload. Type '0', '1', '2', etc. ")
    while True:
        try:
            encrypt()
            if encrypt.file_upload_input < 0:
                print("Please choose a valid number within range.")
                continue
            print(f"You have chosen to upload: {upload.encrypted_file}")
            break
        except IndexError:
            print("Please choose a valid number within range.")
            continue
        except ValueError:
            print("Please type a number, not a string.")
            continue
    sftp_upload()


def download():
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


def sftp_upload():
    if sftp.isfile(upload.encrypted_file) is True:
        while True:
            file_overwrite = input(f"{upload.encrypted_file} exists already on the server. Would you like to overwrite the file? (yes/no)\n ")
            if file_overwrite.lower() == "yes":
                sftp.put(upload.encrypted_file)
                print(f"Uploaded and replaced file: {upload.encrypted_file}")
                os.remove(upload.encrypted_file)
                print(f"{upload.encrypted_file} deleted from disc.")
                break
            elif file_overwrite.lower() == "no":
                print("Upload cancelled.")
                break
            else:
                print("Please enter 'yes' or 'no'. ")
                continue
    else:
        sftp.put(upload.encrypted_file)
        print(f"Uploaded file: {upload.encrypted_file}")
        os.remove(upload.encrypted_file)
        print(f"{upload.encrypted_file} deleted from disc.")
    list_server_files()


def sftp_download():
    if os.path.isfile(download.file_download) is True:
        while True:
            file_overwrite = input(f"{download.file_download} exists already in current working directory. Would you like to overwrite the file? (yes/no)\n ")
            if file_overwrite.lower() == "yes":
                sftp.get(download.file_download)
                print(f"Downloaded and replaced file: {download.file_download}")
                break
            elif file_overwrite.lower() == "no":
                print("Download cancelled.")
                break
            else:
                print("Please enter 'yes' or 'no'. ")
                continue
    else:
        sftp.get(download.file_download)
        print(f"Downloaded file: {download.file_download}")
    list_local_files()


def remove():
    list_server_files()
    if len(list_server_files.server_files) == 0:
        print("No files found.\n--------------")
        select_mode()
    else:
        print("Choose the file you want to remove. Type '0', '1', '2', etc. ")
        while True:
            try:
                file_remove_input = int(input())
                file_remove = list_server_files.server_files[file_remove_input]
                if file_remove_input < 0:
                    print("Please choose a valid number within range.")
                    continue
                print(f"You have chosen to remove: {file_remove}")
                break
            except IndexError:
                print("Please choose a valid number within range.")
                continue
            except ValueError:
                print("Please type a number, not a string.")
                continue
        sftp.remove(file_remove)
        print(f"{file_remove} has been removed from the server.")
        list_server_files()


def select_mode():
    mode = ""
    while mode.lower() not in ("up", "down", "remove", "exit"):
        mode = input("What would you like to do? \nType 'up', if you would like to upload a file. \nType 'down', if you would like to download a file. \nType 'remove', if you would like to remove a file from the server. \nType 'exit', if you would like to end the session.\n")
        if mode == "up":
            upload()
            print("Job completed.\n--------------")
            select_mode()
        if mode == "down":
            list_server_files()
            if len(list_server_files.server_files) == 0:
                print("No files found.\n--------------")
            else:
                download()
                decrypt()
                print("Job completed.\n--------------")
            select_mode()
        if mode == "remove":
            list_server_files()
            if len(list_server_files.server_files) == 0:
                print("No files found.\n--------------")
            else:
                remove()
                print("Job completed.\n--------------")
            select_mode()
        if mode == "exit":
            input("Connection closed. Press enter to exit session.\n")
            break


# Ignore hostkeys
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

# Initiate SFTP connection
try:
    with pysftp.Connection(sftp_config.dnshost, username=sftp_config.username, password=sftp_config.password, port=sftp_config.port, cnopts=cnopts) as sftp:
        with sftp.cd("Note_Backups"):
            print(f"Connection to {sftp_config.dnshost}:{sftp_config.port} established. Directory: {sftp.getcwd()}")
            select_mode()
except SSHException:
    print(f"Unable to connect to {sftp_config.dnshost}. Verify if the server is running.")
