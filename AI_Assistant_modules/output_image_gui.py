import gradio as gr

javascript = """
function copyToClipboard() {
    var img = Array.from(document.querySelectorAll('.output-image img') || []).filter(img => img.offsetParent)[0];
    if (!img) {
        return;
    }
    fetch(img.src)
    .then(response => response.blob())
    .then(blob => {
        const item = new ClipboardItem({ "image/png": blob });
        navigator.clipboard.write([item]);
    })
    .catch(console.error);
}
"""

class OutputImage:
    def __init__(self, transfer_target=None):
        self.transfer_target = transfer_target

    def layout(self, lang_util):
        self.output_image = gr.Image(label=lang_util.get_text("output_image"), interactive=False, elem_classes=["output-image"])
        clipboard_button = gr.Button(""+lang_util.get_text("clipboard"), elem_classes=["clipboard"])
        clipboard_button.click(self._notify, inputs=[self.output_image], _js=javascript)
        if self.transfer_target is not None:
            transfer_button = gr.Button(lang_util.get_text(self.transfer_target.lang_key))
            transfer_button.click(self.transfer_target.accept_transfer, inputs=[self.output_image])
        return self.output_image

    def _notify(self, output_image):
        if output_image is None:
            gr.Warning("Please Image Select")
        else:
            gr.Info("Image Copied to Clipboard")
