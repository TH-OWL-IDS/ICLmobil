/*
 * Copyright 2025 Sascha Martinetz - Fraunhofer IOSB-INA
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

const rollup = require('rollup');
const fs = require('fs');
const path = require('path');

const build = async () => {
  // rebuild JS without modules
  let entry = fs
    .readdirSync(path.resolve(__dirname, '../cordova/www/assets'))
    .filter((f) => f.includes('index') && f.includes('.js'))[0];
  const hash = entry.split('index')[1].split('.js')[0];

  const bundle = await rollup.rollup({
    input: path.resolve(__dirname, '../cordova/www/assets/', entry),
  });
  await bundle.write({
    file: path.resolve(__dirname, '../cordova/www/assets/', `index.${hash}.js`),
    format: 'iife',
    name: 'MyApp',
    sourcemap: false,
  });

  // Remove old chunk files
  fs.readdirSync(path.resolve(__dirname, '../cordova/www/assets')).forEach((f) => {
    if (f.includes('.js') && f.split('.').length > 2 && f !== `index.${hash}.js`) {
      fs.rmSync(path.resolve(__dirname, '../cordova/www/assets', f));
    }
  });

  // fix index.html
  const indexPath = path.resolve(__dirname, '../cordova/www/index.html');
  const indexContent = fs
    .readFileSync(indexPath, 'utf8')
    .split('\n')
    .map((line) => {
      if (line.includes('<link rel="modulepreload"')) return '';
      if (line.includes('<script type="module"')) return '';
      if (line.includes('</body>'))
        return `  <script src="assets/index.${hash}.js"></script>\n</body>`;
      return line;
    })
    .join('\n');
  fs.writeFileSync(indexPath, indexContent);
};

build();
