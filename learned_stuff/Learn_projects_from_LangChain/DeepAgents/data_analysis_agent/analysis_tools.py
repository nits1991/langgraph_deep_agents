"""Additional Tools for analysis"""

@tool(parse_docstring=True)
def slack_send_msg(
    text: str,
    file_path:str|None = None
)-> str:
    """Send message, optionally including attachments such as images.

    Args:
        text: (str) text content of the message
        file_path: (str) file path of attachment in the filesystem.
    """
    # if file path is none
    channel="C0BA8DU1ELV"
    if not file_path:
        slack_client.chat_postMessage(channel=channel,text=text)
    else:
        fp = backend.download_files(
            [file_path]
        )
        slack_client.files_upload_v2(
            channel=channel,
            content=fp[0].content,
            initial_comment=text
        )

    return "Message Sent"
