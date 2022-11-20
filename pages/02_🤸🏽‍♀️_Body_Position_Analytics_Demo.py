import streamlit as st
import boto3
import io
import components.authenticate as authenticate
from dotenv import load_dotenv
import os
import json
st.set_page_config(
    page_title="BPA",
    page_icon="👾",
    layout="wide",
)

load_dotenv()



def downloadBucketFile(filename):
    s3= boto3.client('s3',
        aws_access_key_id=os.environ.get('S3_KEY'),
        aws_secret_access_key=os.environ.get('S3_SECRET')
    )
    data = io.BytesIO()
    video = s3.download_fileobj("code-bear-aws-badr",filename,data)
    data.seek(0)
    #print(data.read())
    return data

def getBucketFiles(email):
    session = boto3.Session(
        aws_access_key_id=os.environ.get('S3_KEY'),
        aws_secret_access_key=os.environ.get('S3_SECRET')
    )
    s3 = session.resource('s3')
    mybucket = s3.Bucket("code-bear-aws-badr")
    bucket_prefix=email+"/"
    objs = mybucket.objects.filter(
    Prefix = bucket_prefix)

    return objs

def sendSQS(user_email,videotitle):
    sqs_client = boto3.client("sqs", region_name="eu-central-1",aws_access_key_id=os.environ['S3_KEY'],
        aws_secret_access_key=os.environ['S3_SECRET'])
    filename = str(user_email)+'/'+str(videotitle)+'.mp4'
    #print(filename)
    message = {"text": filename}
    response = sqs_client.send_message(
        QueueUrl=os.environ['WORKERQUEUE'],
        MessageBody=json.dumps(message)
    )
    #print(response)
    return response

def uploadMP4ToS3(mp4file,user_email,videotitle):
    session = boto3.Session(
        aws_access_key_id=os.environ.get('S3_KEY'),
        aws_secret_access_key=os.environ.get('S3_SECRET')
    )


    s3 = session.resource('s3')
    bucket = s3.Bucket("code-bear-aws-badr")

    #bucket.upload_fileo(Key="test_fileobj.mp4",Filename="./test.mp4")
    try:
        bucket.upload_fileobj(mp4file, str(user_email)+'/'+str(videotitle)+'.mp4')
        st.success('File Successfully Uploaded')
        return True
    except FileNotFoundError:
        st.error('File not found.')
        return False



# Check authentication when user lands on the home page.
authenticate.set_st_state_vars()

# Add login/logout buttons
if st.session_state["authenticated"]:
    user_email=st.session_state["user_info"]["email"]
    st.sidebar.header("Account")
    st.sidebar.write("User Email")
    st.sidebar.code(user_email,language="markdown")
    authenticate.button_logout()
else:
    authenticate.button_login()


st.markdown("# Body Pose Analytics ")


#st.title("Football Video Analytics Powered by Artificial Intelligence")
if (
    st.session_state["authenticated"]
    #and "Underwriters" in st.session_state["user_cognito_groups"]
):
    
    colstop = st.columns(2)
    container1 = colstop[0].container()
    container1.subheader("Step 1: Please Upload your video files here")
    my_expander1 = container1.expander("Click to Expand Step 1", expanded=False)
    with my_expander1:
        #cols = st.columns(4)
        uploaded_mp4 = my_expander1.file_uploader("Select an MP4 file")
        videotitle= my_expander1.text_input('Video Title', 'Video0')
        
        if uploaded_mp4 and user_email is not None:
            
            if uploaded_mp4.type != "video/mp4":
                container1.error('Only MP4 videos are supported. Please upload a different file')
                
            else:
                container1.warning("["+uploaded_mp4.name + '] selected. \n'+'Click on the button below to start processing.')
                #bytes_data = uploaded_mp4.getvalue()
                if container1.button('Upload and Send for Processing'):
                    if user_email !="" and videotitle!="":
                        with st.spinner('Uploading...'):
                            uploadMP4ToS3(uploaded_mp4,user_email,videotitle)
                            response = sendSQS(user_email,videotitle)
                            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                                st.success("Succesfully uploaded video. Please wait 2-5 mins and refresh the video list below.")
                            else:
                                st.error("Error uploading video file. Contact Support")
                    else:
                        st.error("Please Type Video Title")
    container2 = colstop[1].container()
    container2.subheader("Step 2: Choose your videos to display")
    my_expander2 = container2.expander("Click to Expand Step 2", expanded=False)
    with my_expander2:
        fetchbutton = my_expander2.button("Refresh Video List")
        filenames = getBucketFiles(user_email)
        videos=[]
        if fetchbutton:
            filenames = getBucketFiles(user_email)
            videos=[]
        for filename in filenames:
            videos.append(filename.key)

        optionvideo = my_expander2.selectbox("Your Videos: (NOTE: Processing usually takes 5-10 mins after Step 1[Upload]) ",videos)

    
    container3 = st.container()
    container3.subheader("Step 3: Display your video")
    my_expander3 = st.expander("Click to Expand Step 3", expanded=False)
    with my_expander3:
        if my_expander3.button('Display Video: ' + str(optionvideo)):
            if str(optionvideo)!="":
                try:
                    with st.spinner('Loading Video...'):
                        my_expander3.video(downloadBucketFile(str(optionvideo)))
                except:
                    st.error("Couldn't retrieve video")
            else:
                st.error("No video to display")

    
    
else:
    if st.session_state["authenticated"]:
        st.write("You do not have access. Please contact the administrator.")
    else:
        st.write("Please login!")  