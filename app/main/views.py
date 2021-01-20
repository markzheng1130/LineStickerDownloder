from flask import send_file, render_template, current_app

from app.main import blueprint_main as main
from app.main.forms import WebStoreForm
from app.main.url_parser import StickerParser


@main.route('/', methods=['GET', 'POST'])
def index():
    form = WebStoreForm()
    web_store_url = None
    sticker_parser = StickerParser()

    # When POST
    if form.validate_on_submit():
        try:
            web_store_url = form.web_store_url.data.strip()
            form.web_store_url.data = ''

            # Start to parse
            try:
                sticker_parser.parse(web_store_url)
            except Exception as e:
                current_app.logger.error(f'[Exception][{e}]')
                return render_template("400.html", e=e), 400

            sticker_parser.download()
            sticker_parser.generate_zip_file()
            return send_file(sticker_parser.zip_file,
                             mimetype='application/zip',
                             as_attachment=True,
                             attachment_filename=sticker_parser.zip_file_name)

        except Exception as e:
            current_app.logger.error(f'[Exception][{e}]')
            return render_template("500.html", e=e), 500

    # When GET
    return render_template('index.html', form=form,
                           web_store_url=web_store_url,
                           sticker_title=sticker_parser.sticker_title,
                           sticker_url_list=sticker_parser.sticker_url_list)
