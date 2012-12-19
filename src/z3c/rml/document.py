##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""RML ``document`` element

$Id$
"""
__docformat__ = "reStructuredText"
import cStringIO
import sys
import zope.interface
import reportlab.pdfgen.canvas
from reportlab.pdfbase import pdfmetrics, ttfonts, cidfonts
from reportlab.lib import colors, fonts

from z3c.rml import attr, canvas, directive, interfaces, occurence
from z3c.rml import pdfinclude, storyplace, stylesheet, template


class IRegisterType1Face(interfaces.IRMLDirectiveSignature):
    """Register a new Type 1 font face."""

    afmFile = attr.String(
        title=u'AFM File',
        description=u'Path to AFM file used to register the Type 1 face.',
        required=True)

    pfbFile = attr.String(
        title=u'PFB File',
        description=u'Path to PFB file used to register the Type 1 face.',
        required=True)

class RegisterType1Face(directive.RMLDirective):
    signature = IRegisterType1Face

    def process(self):
        args = self.getAttributeValues(valuesOnly=True)
        face = pdfmetrics.EmbeddedType1Face(*args)
        pdfmetrics.registerTypeFace(face)


class IRegisterFont(interfaces.IRMLDirectiveSignature):
    """Register a new font based on a face and encoding."""

    name = attr.String(
        title=u'Name',
        description=(u'The name under which the font can be used in style '
                     u'declarations or other parameters that lookup a font.'),
        required=True)

    faceName = attr.String(
        title=u'Face Name',
        description=(u'The name of the face the font uses. The face has to '
                     u'be previously registered.'),
        required=True)

    encName = attr.String(
        title=u'Encoding Name',
        description=(u'The name of the encdoing to be used.'),
        required=True)

class RegisterFont(directive.RMLDirective):
    signature = IRegisterFont

    def process(self):
        args = self.getAttributeValues(valuesOnly=True)
        font = pdfmetrics.Font(*args)
        pdfmetrics.registerFont(font)


class IAddMapping(interfaces.IRMLDirectiveSignature):
    """Map various styles(bold, italic) of a font name to the actual ps fonts
    used."""

    faceName = attr.String(
        title=u'Name',
        description=(u'The name of the font to be mapped'),
        required=True)

    bold = attr.Integer(
        title=u'Bold',
        description=(u'Bold'),
        required=True)

    italic = attr.Integer(
        title=u'Italic',
        description=(u'Italic'),
        required=True)

    psName = attr.String(
        title=u'psName',
        description=(u'Actual font name mapped'),
        required=True)

class AddMapping(directive.RMLDirective):
    signature = IAddMapping

    def process(self):
        args = self.getAttributeValues(valuesOnly=True)
        fonts.addMapping(*args)

class IRegisterTTFont(interfaces.IRMLDirectiveSignature):
    """Register a new TrueType font given the TT file and face name."""

    faceName = attr.String(
        title=u'Face Name',
        description=(u'The name of the face the font uses. The face has to '
                     u'be previously registered.'),
        required=True)

    fileName = attr.String(
        title=u'File Name',
        description=u'File path of the of the TrueType font.',
        required=True)

class RegisterTTFont(directive.RMLDirective):
    signature = IRegisterTTFont

    def process(self):
        args = self.getAttributeValues(valuesOnly=True)
        font = ttfonts.TTFont(*args)
        pdfmetrics.registerFont(font)


class IRegisterCidFont(interfaces.IRMLDirectiveSignature):
    """Register a new CID font given the face name."""

    faceName = attr.String(
        title=u'Face Name',
        description=(u'The name of the face the font uses. The face has to '
                     u'be previously registered.'),
        required=True)

class RegisterCidFont(directive.RMLDirective):
    signature = IRegisterCidFont

    def process(self):
        args = self.getAttributeValues(valuesOnly=True)
        font = cidfonts.UnicodeCIDFont(*args)
        pdfmetrics.registerFont(font)


class IRegisterFontFamily(interfaces.IRMLDirectiveSignature):
    """Register a new font family."""

    name = attr.String(
        title=u'Name',
        description=(u'The name of the font family.'),
        required=True)

    normal = attr.String(
        title=u'Normal Font Name',
        description=(u'The name of the normal font variant.'),
        required=False)

    bold = attr.String(
        title=u'Bold Font Name',
        description=(u'The name of the bold font variant.'),
        required=False)

    italic = attr.String(
        title=u'Italic Font Name',
        description=(u'The name of the italic font variant.'),
        required=False)

    boldItalic = attr.String(
        title=u'Bold/Italic Font Name',
        description=(u'The name of the bold/italic font variant.'),
        required=True)

class RegisterFontFamily(directive.RMLDirective):
    signature = IRegisterFontFamily

    def process(self):
        args = self.getAttributeValues(valuesOnly=True)
        pdfmetrics.registerFontFamily(*args)


class IColorDefinition(interfaces.IRMLDirectiveSignature):
    """Define a new color and give it a name to be known under."""

    id = attr.String(
        title=u'Id',
        description=(u'The id/name the color will be available under.'),
        required=True)

    RGB = attr.Color(
        title=u'RGB Color',
        description=(u'The color value that is represented.'),
        required=False)

    CMYK = attr.Color(
        title=u'CMYK Color',
        description=(u'The color value that is represented.'),
        required=False)

    value = attr.Color(
        title=u'Color',
        description=(u'The color value that is represented.'),
        required=False)

    spotName = attr.String(
        title=u'Spot Name',
        description=(u'The Spot Name of the CMYK color.'),
        required=False)

    density = attr.Float(
        title=u'Density',
        description=(u'The color density of the CMYK color.'),
        min=0.0,
        max=1.0,
        required=False)

    knockout = attr.String(
        title=u'Knockout',
        description=(u'The knockout of the CMYK color.'),
        required=False)

    alpha = attr.Float(
        title=u'Alpha',
        description=(u'The alpha channel of the color.'),
        min=0.0,
        max=1.0,
        required=False)

class ColorDefinition(directive.RMLDirective):
    signature = IColorDefinition

    def process(self):
        kwargs = dict(self.getAttributeValues())
        id = kwargs.pop('id')
        for attrName in ('RGB', 'CMYK', 'value'):
            color = kwargs.pop(attrName, None)
            if color is not None:
                # CMYK has additional attributes.
                for name, value in kwargs.items():
                    setattr(color, name, value)
                manager = attr.getManager(self)
                manager.colors[id] = color
                return
        raise ValueError('At least one color definition must be specified.')


class IDocInit(interfaces.IRMLDirectiveSignature):
    occurence.containing(
        occurence.ZeroOrMore('registerType1Face', IRegisterType1Face),
        occurence.ZeroOrMore('registerFont', IRegisterFont),
        occurence.ZeroOrMore('registerTTFont', IRegisterTTFont),
        occurence.ZeroOrMore('registerCidFont', IRegisterCidFont),
        occurence.ZeroOrMore('registerFontFamily', IRegisterFontFamily),
        occurence.ZeroOrMore('color', IColorDefinition),
        occurence.ZeroOrMore('addMapping', IAddMapping),
        )

class DocInit(directive.RMLDirective):
    signature = IDocInit
    factories = {
        'registerType1Face': RegisterType1Face,
        'registerFont': RegisterFont,
        'registerTTFont': RegisterTTFont,
        'registerCidFont': RegisterCidFont,
        'color': ColorDefinition,
        'addMapping': AddMapping,
        }


class IDocument(interfaces.IRMLDirectiveSignature):
    occurence.containing(
        occurence.ZeroOrOne('docinit', IDocInit),
        occurence.ZeroOrOne('stylesheet', stylesheet.IStylesheet),
        occurence.ZeroOrOne('template', template.ITemplate),
        occurence.ZeroOrOne('story', template.IStory),
        occurence.ZeroOrOne('pageInfo', canvas.IPageInfo),
        occurence.ZeroOrMore('pageDrawing', canvas.IPageDrawing),
        )

    filename = attr.String(
        title=u'File Name',
        description=(u'The default name of the output file, if no output '
                     u'file was provided.'),
        required=True)

    debug = attr.Boolean(
        title=u'Debug',
        description=u'A flag to activate the debug output.',
        required=False)

    compression = attr.BooleanWithDefault(
        title=u'Compression',
        description=(u'A flag determining whether page compression should '
                     u'be used.'),
        required=False)

    invariant = attr.BooleanWithDefault(
        title=u'Invariant',
        description=(u'A flag that determines whether the produced PDF '
                     u'should be invariant with respect to the date and '
                     u'the exact contents.'),
        required=False)

class Document(directive.RMLDirective):
    signature = IDocument
    zope.interface.implements(interfaces.IManager,
                              interfaces.IPostProcessorManager,
                              interfaces.ICanvasManager)

    factories = {
        'docinit': DocInit,
        'stylesheet': stylesheet.Stylesheet,
        'template': template.Template,
        'story': template.Story,
        'pageInfo': canvas.PageInfo,
        'pageDrawing': canvas.PageDrawing,
        }

    def __init__(self, element):
        super(Document, self).__init__(element, None)
        self.names = {}
        self.styles = {}
        self.colors = {}
        self.postProcessors = []
        self.filename = '<unknown>'

    def process(self, outputFile=None):
        """Process document"""
        # Reset all reportlab global variables. This is very important for
        # ReportLab not to fail.
        reportlab.rl_config._reset()

        # Add our colors mapping to the default ones.
        colors.toColor.setExtraColorsNameSpace(self.colors)

        if outputFile is None:
            # TODO: This is relative to the input file *not* the CWD!!!
            outputFile = open(self.element.get('filename'), 'wb')

        # Create a temporary output file, so that post-processors can
        # massage the output
        self.outputFile = tempOutput = cStringIO.StringIO()

        # Process common sub-directives
        self.processSubDirectives(select=('docinit', 'stylesheet'))

        # Handle Page Drawing Documents
        if self.element.find('pageDrawing') is not None:
            kwargs = dict(self.getAttributeValues(
                select=('compression', 'debug'),
                attrMapping={'compression': 'pageCompression',
                             'debug': 'verbosity'}
                ))

            self.canvas = reportlab.pdfgen.canvas.Canvas(tempOutput, **kwargs)
            self.processSubDirectives(select=('pageInfo', 'pageDrawing'))
            self.canvas.save()

        # Handle Flowable-based documents.
        elif self.element.find('template') is not None:
            self.processSubDirectives(select=('template', 'story'))
            self.doc.multiBuild(self.flowables)

        # Process all post processors
        for name, processor in self.postProcessors:
            tempOutput.seek(0)
            tempOutput = processor.process(tempOutput)

        # Save the result into our real output file
        tempOutput.seek(0)
        outputFile.write(tempOutput.getvalue())

        # Cleanup.
        colors.toColor.setExtraColorsNameSpace({})

