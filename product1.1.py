import streamlit as st
import paramiko

# Konfigurasi server
SERVER_IP = "10.20.12.126"
SERVER_PORT = 22
SERVER_USERNAME = "root"
SERVER_PASSWORD = "20413*26"
WEB_SERVER_PATH = "/var/www/html"

# Perintah SSH
def execute_ssh_command(command):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(SERVER_IP, port=SERVER_PORT, username=SERVER_USERNAME, password=SERVER_PASSWORD)
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        client.close()
        return output, error
    except Exception as e:
        return None, str(e)

# Fungsi untuk mengunggah file ke server
def upload_file(local_path, remote_path):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(SERVER_IP, port=SERVER_PORT, username=SERVER_USERNAME, password=SERVER_PASSWORD)
        sftp = client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        client.close()
        return True, None
    except Exception as e:
        return False, str(e)

# Streamlit app
st.title("Auto Deploy HTdocs to Web Server")

# Upload file
st.text("File requirements:")


uploaded_file = st.file_uploader("Upload File", type=["zip"])

if uploaded_file is not None:
    # Simpan file yang diunggah
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Path file sementara
    local_file_path = uploaded_file.name

    # Konfirmasi upload
    if st.button("Deploy"):
        # Upload file ke server
        remote_file_path = f"{WEB_SERVER_PATH}/{uploaded_file.name}"
        upload_success, upload_error = upload_file(local_file_path, remote_file_path)

        if upload_success:
            # Ekstrak file
            extract_command = f"cd {WEB_SERVER_PATH} && unzip {uploaded_file.name}"
            extract_output, extract_error = execute_ssh_command(extract_command)

            if extract_error:
                st.error(f"Failed to extract file: {extract_error}")
            else:
                # Restart web server
                restart_command = "sudo systemctl restart apache2"
                restart_output, restart_error = execute_ssh_command(restart_command)

                if restart_error:
                    st.error(f"Failed to restart web server: {restart_error}")
                else:
                    st.success("Deploy to " + WEB_SERVER_PATH + " success !")
        else:
            st.error(f"Failed to upload file: {upload_error}")

# Tambahkan opsi untuk menghapus file yang diunggah
st.write("Delete file that has been uploaded to server:")
if st.button("Delete"):
    # Hapus file lokal
    import os
    os.remove(local_file_path)
    st.write("File Deleted.")