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

// Test 1: Toolbar
describe('Toolbar', () => {
    it('check if all toolbar items are visible', () => {
        cy.visit('/');
        cy.get('.toolbar-inner').should('be.visible');
        cy.containsAny('#tab1 > .tabbar-label', ['Start', 'Home']);
        cy.containsAny('#tab2 > .tabbar-label', ['Planen', 'Planning']);
        cy.containsAny('#tab3 > .tabbar-label', ['Aktivität', 'Activity']);
        cy.containsAny('#tab4 > .tabbar-label', ['Konto', 'Account']);
    });
    it('check if all toolbar icons are visible', () => {
        cy.visit('/');
        cy.get('.toolbar-inner').should('be.visible');
        cy.contains('#tab1 > .icon', 'house_alt_fill ');
        cy.contains('#tab2 > .icon', 'map_fill');
        cy.contains('#tab3 > .icon', 'square_list_fill');
        cy.contains('#tab4 > .icon', 'person_crop_circle');
    });
});