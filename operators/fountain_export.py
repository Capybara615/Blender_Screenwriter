import bpy, os, sys

from bpy.props import BoolProperty, StringProperty, EnumProperty
from bpy_extras.io_utils import ExportHelper
from pathlib import Path


class SCREENWRITER_OT_export(bpy.types.Operator, ExportHelper):
    """Export Screenplay"""
    bl_idname = "export.screenplay"
    bl_label = "Export"

    filename_ext = ""

    filter_glob: StringProperty(
        default="*.html;*.pdf;*.fdx",
        options={'HIDDEN'},
        maxlen=255,
    )
    # ("PDF", "pdf", "Exports pdf"), #not working currently
    opt_exp: EnumProperty(
        items=(("HTML", "Html", "Exports html"), ("PDF", "pdf", "Exports pdf"), ("FDX", "fdx", "Final Draft")),
        name="Export Data Type",
        description="Choose what format to export ",
        default="HTML")
    open_browser: BoolProperty(
        name="Open in Browser",
        description="Open exported html or pdf in browser",
        default=True,
    )

    # @classmethod
    # def poll(cls, context):
        # space = bpy.context.space_data
        # try: 
            # filepath = bpy.context.area.spaces.active.text.filepath
            # if filepath.strip() == "": return False
            # return ((space.type == 'TEXT_EDITOR')
                    # and Path(filepath).suffix == ".fountain")
        # except AttributeError: return False

    def execute(self, context):
        return screenplay_export(context, self.filepath, self.opt_exp,
                                 self.open_browser)

def screenplay_export(context, screenplay_filepath, opt_exp, open_browser):

    import subprocess, pip, os
    dir = os.path.dirname(bpy.data.filepath)
    if not dir in sys.path:
        sys.path.append(dir)

    fountain_script = bpy.context.area.spaces.active.text.as_string()
    if fountain_script.strip() == "": return {"CANCELLED"}

    # screenplain
    try:
        import screenplain.parsers.fountain as fountain
    except ImportError:
        pybin = bpy.app.binary_path_python
        subprocess.check_call([pybin, '-m', 'pip', 'install', 'screenplain[PDF]'])
        import screenplain.parsers.fountain as fountain

    from io import StringIO
    import webbrowser
    s = StringIO(fountain_script)
    screenplay = fountain.parse_lines(s)
    output = StringIO()
    if opt_exp == "HTML":
        from screenplain.export.html import convert
        convert(screenplay, output, bare=False)
    if opt_exp == "FDX":
        from screenplain.export.fdx import to_fdx
        to_fdx(screenplay, output)
    if opt_exp == "PDF":
        from screenplain.export.pdf import to_pdf
        to_pdf(screenplay, output)
    sp_out = output.getvalue()
    filename, extension = os.path.splitext(screenplay_filepath)
    fileout_name = filename + "." + opt_exp.lower()
    file = open(fileout_name, "w")
    file.write(sp_out)
    file.close()
    if open_browser:
        if opt_exp == "HTML" or opt_exp == "PDF":
            webbrowser.open(fileout_name)

    return {'FINISHED'}
