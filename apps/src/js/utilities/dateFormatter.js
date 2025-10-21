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

export function formatDate(timestamp, locale) {
  let date;

  // Überprüfen, ob der Timestamp ein Unix-Timestamp (INT) oder ein ISO-String ist
  if (typeof timestamp === 'number') {
    date = new Date(timestamp); // Unix-Timestamp
  } else if (typeof timestamp === 'string') {
    date = new Date(timestamp); // ISO-8601-String
  } else {
    throw new Error(`Invalid timestamp: ${timestamp}`);
  }
  
  // Define date formatting options for the shortened format
  const options = {
    weekday: 'long', // Full weekday name (e.g., "Donnerstag")
    year: '2-digit', // Short year (e.g., "24")
    month: '2-digit', // Month as 2 digits (e.g., "12" for December)
    day: '2-digit', // Day as 2 digits (e.g., "16")
  };

  // Format the date based on the locale
  const formattedDate = new Intl.DateTimeFormat(locale, options).format(date);

  // Return the formatted date string
  return formattedDate;
}