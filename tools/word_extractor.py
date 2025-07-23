from collections.abc import Generator
from typing import Any, Optional
import tempfile
import os

import docx2txt
from dify_plugin.entities import I18nObject
from dify_plugin.entities.tool import ToolInvokeMessage, ToolParameter
from dify_plugin import Tool
from dify_plugin.file.file import File


class WordExtractorTool(Tool):
    """
    A tool for extracting text and images from Word files.
    This tool takes a Word file as input and returns the extracted text and images.
    """

    def _invoke(
        self,
        tool_parameters: dict[str, Any],
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        app_id: Optional[str] = None,
        message_id: Optional[str] = None,
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Extract text and images from a Word file.

        Args:
            tool_parameters (dict[str, Any]): Parameters for the tool
                - word_content (File): Dify File object containing the Word document
            user_id (Optional[str]): The ID of the user invoking the tool
            conversation_id (Optional[str]): The conversation ID
            app_id (Optional[str]): The app ID
            message_id (Optional[str]): The message ID

        Returns:
            Generator[ToolInvokeMessage, None, None]: Generator yielding the extracted text and images

        Raises:
            ValueError: If the Word content format is invalid or required parameters are missing
            Exception: For any other errors during Word processing
        """
        try:
            # Get and validate parameters
            word_content = tool_parameters.get("word_content")
            if not isinstance(word_content, File):
                raise ValueError("Invalid Word content format. Expected File object.")

            original_filename = word_content.filename or "document"

            # Create a temporary file to save the Word document
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
                temp_file.write(word_content.blob)
                temp_file_path = temp_file.name

            try:
                # Extract images to a temporary directory
                temp_dir = tempfile.mkdtemp()
                try:
                    # Extract text and images
                    text = docx2txt.process(temp_file_path, temp_dir)
                    yield self.create_text_message(text)

                    # Check if any images were extracted
                    image_files = []
                    if os.path.exists(temp_dir):
                        for file_name in os.listdir(temp_dir):
                            if file_name.lower().endswith(
                                (".png", ".jpg", ".jpeg", ".gif", ".bmp")
                            ):
                                image_files.append(os.path.join(temp_dir, file_name))

                    if image_files:
                        # Send each extracted image
                        for i, image_path in enumerate(image_files):
                            try:
                                with open(image_path, "rb") as img_file:
                                    img_data = img_file.read()

                                # Determine file extension
                                file_ext = os.path.splitext(image_path)[1].lower()
                                if not file_ext:
                                    file_ext = ".png"

                                # Create filename for this image
                                base_filename = original_filename.rsplit(".", 1)[0]
                                output_filename = (
                                    f"{base_filename}_image_{i+1}{file_ext}"
                                )

                                # Determine MIME type
                                mime_types = {
                                    ".png": "image/png",
                                    ".jpg": "image/jpeg",
                                    ".jpeg": "image/jpeg",
                                    ".gif": "image/gif",
                                    ".bmp": "image/bmp",
                                }
                                mime_type = mime_types.get(file_ext, "image/png")

                                # Send the image
                                yield self.create_blob_message(
                                    blob=img_data,
                                    meta={
                                        "mime_type": mime_type,
                                        "file_name": output_filename,
                                    },
                                )
                            except Exception as e:
                                yield self.create_text_message(
                                    f"Error processing image {i+1}: {str(e)}"
                                )

                finally:
                    # Clean up temporary image directory
                    import shutil

                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir)

            finally:
                # Clean up temporary Word file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except ValueError as e:
            raise ValueError(f"Invalid value encountered: {str(e)}")
        except Exception as e:
            raise Exception(f"Error extracting from Word document: {str(e)}")

    def get_runtime_parameters(
        self,
        conversation_id: Optional[str] = None,
        app_id: Optional[str] = None,
        message_id: Optional[str] = None,
    ) -> list[ToolParameter]:
        """
        Get the runtime parameters for the Word extractor tool.

        Returns:
            list[ToolParameter]: List of tool parameters
        """
        parameters = [
            ToolParameter(
                name="word_content",
                label=I18nObject(en_US="Word Content", zh_Hans="Word 内容"),
                human_description=I18nObject(
                    en_US="Word file (.docx) to extract text and images from",
                    zh_Hans="要提取文本和图片的Word文件(.docx)",
                ),
                type=ToolParameter.ToolParameterType.FILE,
                form=ToolParameter.ToolParameterForm.FORM,
                required=True,
                file_accepts=[
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                ],
            ),
        ]
        return parameters
