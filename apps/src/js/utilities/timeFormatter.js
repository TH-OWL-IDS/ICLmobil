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

export function formatTime(timestamp, locale) {
  // Convert string timestamps to numbers
  if (typeof timestamp === 'string') {
    timestamp = new Date(timestamp).getTime(); // Konvertiere ISO-String in Unix-Timestamp
  }

  // Ensure timestamp is a valid number
  if (typeof timestamp !== 'number' || isNaN(timestamp)) {
    throw new Error(`Invalid timestamp: ${timestamp}`);
  }

  const date = new Date(timestamp);

  if (isNaN(date.getTime())) {
    throw new Error(`Invalid Date object created from timestamp: ${timestamp}`);
  }

  const options = locale === 'de'
    ? { hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }
    : { hour: 'numeric', minute: '2-digit', hour12: true };

  const formattedTime = new Intl.DateTimeFormat(locale, options).format(date);

  return locale === 'de' ? `${formattedTime}` + ' Uhr' : formattedTime;
}
