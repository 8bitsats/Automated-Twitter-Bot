import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient


app = func.FunctionApp()

# Schedule timer to execute after every 8 hours
@app.schedule(schedule="0 0 0 * * *", arg_name="myTimer", run_on_startup=True,
				use_monitor=False)

def timer_trigger(myTimer: func.TimerRequest) -> None:
	if myTimer.past_due:
		logging.warning('The timer is past due!')


	# Authenticate Azure
	connection_string = "DefaultEndpointsProtocol=https;AccountName=tweetposts;AccountKey=qG3+CAzcaeGzNsrmDBz5ZvIFbPz89eEaLnfk7nyimjPIRQLEVzMaxYFTOtL4ywpkIKIaHkoTMC/7+AStRWoS1A==;EndpointSuffix=core.windows.net"
	blob_service_client = BlobServiceClient.from_connection_string(connection_string)

	urls = [
			"https://tweetposts.blob.core.windows.net/afcon-2023/text_log.txt",
			"https://tweetposts.blob.core.windows.net/premier-league/text_log.txt"
		]

	for i in urls:
		container_name = i.split("/")[-2]
		blob_name = i.split("/")[-1]
		blob_client = blob_service_client.get_blob_client(container_name, blob_name)

		existing_data = int(blob_client.download_blob().readall().decode('utf-8') if blob_client.exists() else b"")
		new_id=existing_data+1
		blob_client.upload_blob(str(new_id), overwrite=True)
		logging.info(f"New Message ID for {container_name} in {blob_name} is {new_id}")


