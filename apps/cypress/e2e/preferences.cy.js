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

// Custom Params
const testlangde = 1;
const testlangen = 0;
const teststoredest7 = 0;
const teststoredest14 = 1;
const teststoredest30 = 2;
const testmodelight = 0;
const testmodedark = 1;
const testmodesystem = 2;

// Test 1: Preferences page loads
describe('Preferences page loads', () => {
    it('should display the preferences page', () => {
        cy.visit('/preferences');
        cy.containsAny('.title-large-text', ['Einstellungen', 'Preferences']);
    });
});

// Test 2: Test App Settings Fields
describe('App Settings', () => {
    it('should show all app settings fields', () => {
        cy.visit('/preferences');
        cy.get('.page-content').eq(0).scrollTo('top');
        cy.get('[data-cy="prefs-faceid-fld"]').should('be.visible');
        cy.get('[data-cy="prefs-faceid-tgl"] input[type="checkbox"]').check({ force: true });
        cy.wait(500);
        cy.get('[data-cy="prefs-faceid-tgl"] input[type="checkbox"]').uncheck({ force: true });
        cy.get('.page-content').eq(0).scrollTo('top');
        cy.get('[data-cy="prefs-lang-fld"]').should('be.visible');
        cy.get('[data-cy="prefs-lang-fld"] select').select(testlangen, { force: true });
        cy.wait(500);
        cy.get('[data-cy="prefs-lang-fld"] select').select(testlangde, { force: true });
        cy.wait(500);
        cy.get('[data-cy="prefs-store-dest-fld"]').should('be.visible');
        cy.get('[data-cy="prefs-store-dest-fld"] select').select(teststoredest7, { force: true });
        cy.wait(500);
        cy.get('[data-cy="prefs-store-dest-fld"] select').select(teststoredest14, { force: true });
        cy.wait(500);
        cy.get('[data-cy="prefs-store-dest-fld"] select').select(teststoredest30, { force: true });
        cy.wait(500);
        cy.get('[data-cy="prefs-mode-fld"]').should('be.visible');
        cy.get('[data-cy="prefs-mode-fld"] select').select(testmodelight, { force: true });
        cy.wait(500);
        cy.get('[data-cy="prefs-mode-fld"] select').select(testmodedark, { force: true });
        cy.wait(500);
        cy.get('[data-cy="prefs-mode-fld"] select').select(testmodesystem, { force: true });
        cy.wait(500);
        cy.get('[data-cy="prefs-reset-tours-fld"]').should('be.visible');
        cy.get('[data-cy="prefs-reset-tours-fld"]').click();
        cy.wait(500);
        cy.get('.dialog .dialog-button-strong').click();
        cy.get('[data-cy="prefs-pool-setup-fld"]').should('be.visible');
        cy.get('[data-cy="prefs-pool-setup-fld"]').click();
        cy.wait(500);
        cy.get('.left .link').click();
        cy.wait(500);
    });
});

// Test 3: Test App Information Fields
describe('App Information', () => {
    it('should show all app information fields', () => {
        cy.visit('/preferences');
        cy.get('.page-content').eq(0).scrollTo('bottom');
        cy.get('[data-cy="prefs-help-lnk"]').should('be.visible');
        cy.get('[data-cy="prefs-help-lnk"]').click();
        cy.wait(500);
        cy.get('.left .link').click();
        cy.wait(500);
        cy.get('[data-cy="prefs-data-lnk"]').should('be.visible');
        cy.get('[data-cy="prefs-data-lnk"]').click();
        cy.wait(500);
        cy.get('.left .link').click();
        cy.wait(500);
        cy.get('[data-cy="prefs-legal-lnk"]').should('be.visible');
        cy.get('[data-cy="prefs-legal-lnk"]').click();
        cy.wait(500);
        cy.get('.left .link').click();
        cy.wait(500);
        cy.get('[data-cy="prefs-imprint-lnk"]').should('be.visible');
        cy.get('[data-cy="prefs-imprint-lnk"]').click();
        cy.wait(500);
        cy.get('.left .link').click();
        cy.wait(500);
        cy.get('[data-cy="prefs-about-lnk"]').should('be.visible');
        cy.get('[data-cy="prefs-about-lnk"]').click();
        cy.wait(500);
        cy.get('.left .link').click();
        cy.wait(500);
    });
});

//TODO: Add tests for all things AFTER user login!