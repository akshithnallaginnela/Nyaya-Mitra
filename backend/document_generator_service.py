"""
Document Generator Service
Handles document generation from Jinja2 templates with PDF and text output
"""

from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound
from pathlib import Path
from typing import Dict, Any, Tuple
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from io import BytesIO
import re

from templates.template_config import (
    DocumentType,
    get_template_config,
    validate_template_inputs,
    get_all_fields
)


class DocumentGeneratorService:
    """Service for generating legal documents from templates"""
    
    def __init__(self, template_dir: str = None):
        """
        Initialize document generator service
        
        Args:
            template_dir: Directory containing Jinja2 templates (defaults to ./templates)
        """
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"
        else:
            template_dir = Path(template_dir)
        
        self.template_dir = template_dir
        
        # Set up Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def load_template(self, document_type: DocumentType) -> Any:
        """
        Load Jinja2 template for a document type
        
        Args:
            document_type: Type of document to generate
            
        Returns:
            Jinja2 Template object
            
        Raises:
            ValueError: If document type is invalid or template not found
        """
        config = get_template_config(document_type)
        if not config:
            raise ValueError(f"Invalid document type: {document_type}")
        
        template_file = config["template_file"]
        
        try:
            template = self.jinja_env.get_template(template_file)
            return template
        except TemplateNotFound:
            raise ValueError(f"Template file not found: {template_file}")
    
    def validate_inputs(self, document_type: DocumentType, user_inputs: Dict[str, Any]) -> Tuple[bool, list]:
        """
        Validate user inputs against template requirements
        
        Args:
            document_type: Type of document
            user_inputs: Dictionary of user-provided inputs
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        return validate_template_inputs(document_type, user_inputs)
    
    def add_placeholders(self, user_inputs: Dict[str, Any], document_type: DocumentType) -> Dict[str, Any]:
        """
        Add placeholders for missing optional fields
        
        Args:
            user_inputs: Dictionary of user-provided inputs
            document_type: Type of document
            
        Returns:
            Dictionary with placeholders added for missing optional fields
        """
        all_fields = get_all_fields(document_type)
        inputs_with_placeholders = user_inputs.copy()
        
        for field in all_fields:
            if not field.required and field.name not in inputs_with_placeholders:
                # Add placeholder based on field type
                if field.field_type.value == "list":
                    inputs_with_placeholders[field.name] = []
                elif field.field_type.value == "boolean":
                    inputs_with_placeholders[field.name] = False
                else:
                    # Use uppercase placeholder in brackets
                    placeholder = f"[{field.label.upper()}]"
                    inputs_with_placeholders[field.name] = placeholder
        
        # Add current date if date field is missing
        if "date" not in inputs_with_placeholders or not inputs_with_placeholders["date"]:
            inputs_with_placeholders["date"] = datetime.now().strftime("%d %B %Y")
        
        return inputs_with_placeholders
    
    def render_template(self, document_type: DocumentType, user_inputs: Dict[str, Any]) -> str:
        """
        Render template with user data
        
        Args:
            document_type: Type of document to generate
            user_inputs: Dictionary of user-provided inputs
            
        Returns:
            Rendered text document
            
        Raises:
            ValueError: If validation fails or template not found
        """
        # Validate inputs
        is_valid, errors = self.validate_inputs(document_type, user_inputs)
        if not is_valid:
            raise ValueError(f"Validation errors: {', '.join(errors)}")
        
        # Load template
        template = self.load_template(document_type)
        
        # Add placeholders for missing optional fields
        inputs_with_placeholders = self.add_placeholders(user_inputs, document_type)
        
        # Render template
        rendered_text = template.render(**inputs_with_placeholders)
        
        return rendered_text
    
    def generate_pdf(self, text_content: str) -> bytes:
        """
        Generate PDF from text content using ReportLab
        
        Args:
            text_content: Rendered text content
            
        Returns:
            PDF file as bytes
        """
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles for legal documents
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=14,
            textColor='black',
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor='black',
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            textColor='black',
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        )
        
        # Build PDF content
        story = []
        
        # Split content into lines and process
        lines = text_content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if not line:
                # Empty line - add small spacer
                story.append(Spacer(1, 0.1 * inch))
                continue
            
            # Detect headings (all caps or specific patterns)
            if line.isupper() and len(line) < 100:
                # Heading
                story.append(Paragraph(line, heading_style))
            elif line.startswith('Subject:') or line.startswith('Reference:'):
                # Important lines
                story.append(Paragraph(f"<b>{line}</b>", body_style))
            elif line.startswith('From:') or line.startswith('To:'):
                # Address headers
                story.append(Paragraph(f"<b>{line}</b>", body_style))
            elif line.startswith('---'):
                # Separator
                story.append(Spacer(1, 0.2 * inch))
            else:
                # Regular body text
                # Escape special characters for ReportLab
                line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(line, body_style))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def generate_document(
        self,
        document_type: DocumentType,
        user_inputs: Dict[str, Any]
    ) -> Tuple[str, bytes]:
        """
        Generate both text and PDF versions of a document
        
        Args:
            document_type: Type of document to generate
            user_inputs: Dictionary of user-provided inputs
            
        Returns:
            Tuple of (text_content, pdf_bytes)
            
        Raises:
            ValueError: If validation fails or template not found
        """
        # Render text version
        text_content = self.render_template(document_type, user_inputs)
        
        # Generate PDF version
        pdf_bytes = self.generate_pdf(text_content)
        
        return text_content, pdf_bytes


# Singleton instance
_document_generator_service = None


def get_document_generator_service() -> DocumentGeneratorService:
    """
    Get singleton instance of DocumentGeneratorService
    
    Returns:
        DocumentGeneratorService instance
    """
    global _document_generator_service
    if _document_generator_service is None:
        _document_generator_service = DocumentGeneratorService()
    return _document_generator_service
