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

export function formatIcon(type) {
  const icons = {
      sharing: 'electric_scooter',
      scooter: 'electric_scooter',
      bike: 'pedal_bike',
      bus: 'directions_bus',
      walk: 'directions_walk',
      car: 'directions_car',
      pt: 'directions_bus',
      unknown: 'directions_bus'
  };
  return icons[type] || 'directions_car';
}