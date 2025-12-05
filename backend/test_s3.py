import boto3

s3 = boto3.client('s3')

bucket_name = 'agenticai-medical-appointment-system'

# try:
#     s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'ap-south-1'})
#     print(f"Bucket {bucket_name} created successfully")
#     response = s3.list_buckets()
#     print("available buckets: ", response)
# except Exception as e:
#     print(e)
#     print("Error creating bucket")


file_path = 'data/conversation_memory.json'


s3.upload_file(file_path, bucket_name, 'conversation_memory.json')
print(f"File {file_path} uploaded successfully")

response = s3.list_objects_v2(Bucket=bucket_name)
print("files in bucket: ", response['Contents'])

# s3.download_file(bucket_name, file_path, 'data/conversation_memory_downloaded.json')
# print("File downloaded successfully")

# with open('data/conversation_memory_downloaded.json', 'r') as data:
#     print(data.read())

# s3.delete_object(Bucket=bucket_name, Key=file_path)
# print("File deleted successfully")


