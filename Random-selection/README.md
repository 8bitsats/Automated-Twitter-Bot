<h3>How To Upload And Download Files To Azure In Python</h3>
                              	
        
<p>Azure is a cloud storage service provided by Microsoft. Azure provides Python API &#8220;Azure&#8221; to enable Python developers to interact with cloud storage easily. In this  use Azure Python SDK to move files from a local machine to the Azure cloud storage.</p>

<h2 class="has-vivid-cyan-blue-color has-text-color wp-block-heading">Requirements</h2>

<p>For the purposes of this tutorial, you must have Azure installed in your Python environment. You can install the Azure SDK using pip in the following manner:</p>

<pre><code>pip install azure</code></pre>

<p>Further, you must have an Azure account with cloud storage as an active service on it. After all, this tutorial is about understanding how to use Azure Python SDK to move files to the Azure cloud storage. To learn about how to create the Azure account and activate cloud storage, please <a href="https://docs.microsoft.com/en-us/azure/?product=featured" target="_blank" rel="noreferrer noopener">click here</a>. </p>

<p>Let&#8217;s create our first project on the Azure cloud storage named, &#8220;myfirstproject&#8221;. Under that, we create a container named, &#8220;datacourse-007&#8221;. When you create the new account on Azure, it provides you a portal, which you can use to create a project and also create a container in it as shown below:</p>

<figure class="wp-block-image size-large"><img decoding="async" width="1024" height="258"  alt="Azure Python SDK"  data-srcset="https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-17-27-29-1024x258.png 1024w, https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-17-27-29-300x76.png 300w, https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-17-27-29-768x194.png 768w, https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-17-27-29.png 1496w"  data-src="https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-17-27-29-1024x258.png" data-sizes="(max-width: 1024px) 100vw, 1024px" class="wp-image-3166 lazyload" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==" /><noscript><img decoding="async" width="1024" height="258" src="https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-17-27-29-1024x258.png" alt="Azure Python SDK" class="wp-image-3166" srcset="https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-17-27-29-1024x258.png 1024w, https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-17-27-29-300x76.png 300w, https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-17-27-29-768x194.png 768w, https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-17-27-29.png 1496w" sizes="(max-width: 1024px) 100vw, 1024px" /></noscript></figure>

<p>So far we have installed the Azure Python Library using pip, and we have set up the container on the cloud storage account.</p>

<p>Let&#8217;s move forward to our Python programming part.</p>

<h2 class="has-vivid-cyan-blue-color has-text-color wp-block-heading">Upload File To Azure Storage</h2>

<p>When we create a container, Azure provides you a connection string as a secret key, which you can use to access cloud storage from third party apps (in this case our Python program).</p>

<p>So let&#8217;s first import the Azure library in Python and store that connection string in conn_string variable as shown below:</p>

<pre><code>from azure.storage.blob import BlobClient
# paste connection string below
conn_str = "****************************"
</code></pre>

<p>On Azure storage, files are treated as Blobs. So when you upload any file to Azure, it will be referred to as a Blob.</p>

<p>To upload a file as a Blob to Azure, we need to create BlobClient using the Azure library.</p>

<pre><code>blob_client = BlobClient(conn_string=conn_str,container_name="datacourses-007",blob_name="testing.txt")</code></pre>

<p>While creating blob_client, you must pass connection_string, name of container and blob_name as parameter to BlobClient() method.</p>

<p>Once blob_client is created we can open the stream to our file and can call blob_client.upload_data() method to upload content of that file to Azure Blob.</p>

<pre><code># let's upload file to blob

try:
    with open('testing.txt',"rb") as f:
        blob.upload_blob(f)
        print('testing.txt uploaded to container: datacourses-007 successfully')

except Exception as e:
    print(e)</code></pre>

<figure class="wp-block-image size-large"><img decoding="async" width="591" height="19"  alt=""  data-srcset="https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-20-17-41.png 591w, https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-20-17-41-300x10.png 300w"  data-src="https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-20-17-41.png" data-sizes="(max-width: 591px) 100vw, 591px" class="wp-image-3169 lazyload" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==" /><noscript><img decoding="async" width="591" height="19" src="https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-20-17-41.png" alt="" class="wp-image-3169" srcset="https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-20-17-41.png 591w, https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-20-17-41-300x10.png 300w" sizes="(max-width: 591px) 100vw, 591px" /></noscript></figure>

<p>Let&#8217;s verify it by refreshing our container portal on Azure.</p>

<figure class="wp-block-image size-large"><img decoding="async" width="1024" height="304"  alt=""  data-srcset="https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-20-18-53-1024x304.png 1024w, https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-20-18-53-300x89.png 300w, https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-20-18-53-768x228.png 768w, https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-20-18-53.png 1192w"  data-src="https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-20-18-53-1024x304.png" data-sizes="(max-width: 1024px) 100vw, 1024px" class="wp-image-3170 lazyload" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==" /><noscript><img decoding="async" width="1024" height="304" src="https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-20-18-53-1024x304.png" alt="" class="wp-image-3170" srcset="https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-20-18-53-1024x304.png 1024w, https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-20-18-53-300x89.png 300w, https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-20-18-53-768x228.png 768w, https://www.datacourses.com/wp-content/uploads/2021/06/Screenshot-from-2021-06-28-20-18-53.png 1192w" sizes="(max-width: 1024px) 100vw, 1024px" /></noscript></figure>

<p>So here we can see that our testing.txt file is uploaded as a Blob to our container, datacourses-007.</p>

<h2 class="has-vivid-cyan-blue-color has-text-color wp-block-heading">Download File From Azure Container</h2>

<p>Now, we write a program to download a file from the Azure container.</p>

<p>First of all, we import BlobClient from azure.storage.blob and pass our connection_string to variable conn_str.</p>

<pre><code>from azure.storage.blob import BlobClient
# enter your connection string below
conn_str = "**************************"</code></pre>

<p>Now we initiate blob object as following:</p>

<pre><code>blob = BlobClient.from_connection_string(conn_str=conn_str,container_name="datacourses-007", blob_name="testing.txt")
</code></pre>

<p>Open file writer stream with name of file &#8220;downloaded_testing.txt&#8221; and call blob.download_blob() method.</p>

<pre><code>try:
    with open('downloaded_testing.txt',"wb") as f:
        f.write(blob.download_blob().readall())
        print('testing.txt downloaded from container: datacourses-007 successfully')

except Exception as e:
    print(e)</code></pre>

<pre><code>testing.txt downloaded from container: datacourses-007 successfully</code></pre>
