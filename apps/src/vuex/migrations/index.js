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

import { v189 } from './v189'
import { v190 } from './v190'
import { v200 } from './v200'
import { v202 } from './v202'
import { v275 } from './v275'
import { v280 } from './v280'

// Import all migrations
const migrations = [
  v189,
  v190,
  v200,
  v202,
  v275,
  v280
  // Add new migrations here
]

// Sort migrations by version number
export const sortedMigrations = migrations.sort((a, b) => a.version - b.version)