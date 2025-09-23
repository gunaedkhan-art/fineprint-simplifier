# error_handler.py - Comprehensive error handling and user feedback

from typing import Dict, Any
import os
import tempfile

class DocumentAnalysisError(Exception):
    """Custom exception for document analysis errors"""
    def __init__(self, error_type: str, message: str, details: str = None, user_action: str = None):
        self.error_type = error_type
        self.message = message
        self.details = details
        self.user_action = user_action
        super().__init__(self.message)

def handle_upload_error(error_type: str, details: str = None, file_info: Dict = None) -> Dict[str, Any]:
    """
    Handle various upload and processing errors with user-friendly messages
    """
    error_messages = {
        "file_too_large": {
            "error": "File is too large",
            "details": "Please upload a file smaller than 10MB. Large files can be slow to process.",
            "user_action": "Try compressing your document or splitting it into smaller parts."
        },
        "unsupported_format": {
            "error": "Unsupported file format",
            "details": "This file type is not supported. Please use PDF, Word, or image files.",
            "user_action": "Convert your document to PDF, Word (.docx), or image format (.jpg, .png, .tiff)."
        },
        "corrupted_file": {
            "error": "File appears to be corrupted",
            "details": "The uploaded file cannot be read properly.",
            "user_action": "Try downloading the file again or use a different file."
        },
        "no_text_found": {
            "error": "No readable text found",
            "details": "The document doesn't contain any readable text.",
            "user_action": "Ensure your document contains text. For scanned documents, try a higher quality scan."
        },
        "password_protected": {
            "error": "Password-protected document",
            "details": "This document is password-protected and cannot be processed.",
            "user_action": "Remove the password from your document or save it without password protection."
        },
        "processing_timeout": {
            "error": "Processing took too long",
            "details": "The document is too complex or large to process within the time limit.",
            "user_action": "Try uploading a smaller document or contact support for assistance."
        },
        "insufficient_quality": {
            "error": "Document quality too low",
            "details": "The document quality is insufficient for accurate analysis.",
            "user_action": "Upload a higher quality scan or ensure the document is clear and readable."
        },
        "network_error": {
            "error": "Network connection error",
            "details": "There was a problem with the network connection.",
            "user_action": "Check your internet connection and try again."
        },
        "server_error": {
            "error": "Server processing error",
            "details": "An unexpected error occurred while processing your document.",
            "user_action": "Please try again in a few moments. If the problem persists, contact support."
        }
    }
    
    # Get base error info
    error_info = error_messages.get(error_type, {
        "error": "Unknown error",
        "details": "An unexpected error occurred.",
        "user_action": "Please try again or contact support."
    })
    
    # Add file-specific details if available
    if file_info:
        if file_info.get("size"):
            error_info["file_size"] = f"{file_info['size']} bytes"
        if file_info.get("type"):
            error_info["file_type"] = file_info["type"]
        if file_info.get("name"):
            error_info["file_name"] = file_info["name"]
    
    # Add custom details if provided
    if details:
        error_info["details"] = details
    
    return {
        "error": error_info["error"],
        "details": error_info["details"],
        "user_action": error_info["user_action"],
        "error_type": error_type,
        "file_info": file_info or {}
    }

def validate_file_upload(file, max_size_mb: int = 10) -> Dict[str, Any]:
    """
    Validate uploaded file before processing
    """
    file_info = {
        "name": file.filename,
        "size": 0,
        "type": None
    }
    
    # Check if file exists
    if not file or not file.filename:
        return handle_upload_error("no_file", "No file was uploaded.")
    
    # Get file extension
    file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ""
    file_info["type"] = file_ext
    
    # Check file size (if we can get it)
    try:
        # Read file content to check size
        content = file.file.read()
        file_size = len(content)
        file_info["size"] = file_size
        
        # Reset file pointer
        file.file.seek(0)
        
        # Check size limit
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            return handle_upload_error("file_too_large", f"File size: {file_size} bytes, limit: {max_size_bytes} bytes", file_info)
        
    except Exception as e:
        return handle_upload_error("corrupted_file", f"Error reading file: {str(e)}", file_info)
    
    # Check file type
    supported_types = ["pdf", "docx", "jpg", "jpeg", "png", "tiff", "bmp", "gif"]
    if file_ext not in supported_types:
        return handle_upload_error("unsupported_format", f"File type: .{file_ext}", file_info)
    
    return {"valid": True, "file_info": file_info}

def handle_processing_error(error: Exception, file_info: Dict = None) -> Dict[str, Any]:
    """
    Handle errors during document processing
    """
    error_message = str(error).lower()
    
    # Determine error type based on error message
    if "password" in error_message or "encrypted" in error_message:
        return handle_upload_error("password_protected", str(error), file_info)
    elif "timeout" in error_message or "time" in error_message:
        return handle_upload_error("processing_timeout", str(error), file_info)
    elif "quality" in error_message or "readable" in error_message:
        return handle_upload_error("insufficient_quality", str(error), file_info)
    elif "network" in error_message or "connection" in error_message:
        return handle_upload_error("network_error", str(error), file_info)
    else:
        return handle_upload_error("server_error", str(error), file_info)

def create_user_friendly_response(error_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a user-friendly error response
    """
    return {
        "success": False,
        "error": error_dict["error"],
        "details": error_dict["details"],
        "user_action": error_dict["user_action"],
        "error_type": error_dict["error_type"],
        "file_info": error_dict.get("file_info", {}),
        "support_contact": "If you continue to experience issues, please contact support."
    }

def log_error(error: Exception, context: Dict = None):
    """
    Log errors for debugging (in production, this would go to a logging service)
    """
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {}
    }
    
    # In production, this would be sent to a logging service
    print(f"ERROR: {error_info}")

def get_supported_formats_info() -> Dict[str, Any]:
    """
    Get information about supported file formats
    """
    return {
        "supported_formats": [
            {
                "extension": "pdf",
                "name": "PDF Document",
                "description": "Portable Document Format",
                "max_size": "10MB",
                "notes": "Best for text documents. Scanned PDFs are supported with OCR."
            },
            {
                "extension": "docx",
                "name": "Word Document",
                "description": "Microsoft Word Document",
                "max_size": "10MB",
                "notes": "Word documents (.docx format only)."
            },
            {
                "extension": "jpg",
                "name": "JPEG Image",
                "description": "JPEG Image File",
                "max_size": "10MB",
                "notes": "Image files will be processed using OCR."
            },
            {
                "extension": "png",
                "name": "PNG Image",
                "description": "PNG Image File",
                "max_size": "10MB",
                "notes": "Image files will be processed using OCR."
            },
            {
                "extension": "tiff",
                "name": "TIFF Image",
                "description": "TIFF Image File",
                "max_size": "10MB",
                "notes": "High-quality image format, good for scanned documents."
            }
        ],
        "max_file_size": "10MB",
        "processing_time": "Usually 30-60 seconds",
        "quality_requirements": "Clear, readable text with good contrast"
    }
