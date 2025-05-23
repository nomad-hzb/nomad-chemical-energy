# MIT License

# Copyright (c) 2019

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import tempfile

import yadg


def get_header_and_data(file):
    file_content = file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mpr') as temp_file:
        temp_file.write(file_content)
        temp_file_path = temp_file.name

    try:
        data_tree = yadg.extractors.extract(filetype='eclab.mpr', path=temp_file_path)
    except Exception as e:
        print(f'Error during extraction: {e}')
        return None, None

    metadata = json.loads(data_tree.attrs.get('original_metadata'))
    return metadata, data_tree
