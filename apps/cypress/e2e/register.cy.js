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
const testname = 'cypress testuser';
const testemail = 'info@hangar18.com';
const testphone = '+491752897441';
const testpassword = 'test1234';
const testrelation = 2;

// Test 1: Register page loads
describe('Register page loads', () => {
    it('should display the register page', () => {
        cy.visit('/register');
        cy.containsAny('.title-large-text', ['Registrierung', 'Register']);
    });
});

// Test 2: Enter registration data
describe('Register Test', () => {
    it('enter data for test user and register', () => {
        cy.visit('/register');
        cy.get('[data-cy="register-avatar-lnk"]').click({ force: true });
        cy.wait(500);
        cy.get('.actions-modal .actions-button').contains('Cancel').click();
        cy.wait(500);

        cy.get('[data-cy="register-name-fld"] input').type(testname, { force: true });
        cy.get('[data-cy="register-email-fld"] input').type(testemail, { force: true });
        cy.get('[data-cy="register-phone-fld"] input').type(testphone, { force: true });

        cy.get('.page-content').eq(0).scrollTo('bottom');

        cy.get('[data-cy="register-pwd-fld"] input').type(testpassword, { force: true });
        cy.get('[data-cy="register-pwd-repeat-fld"] input').type(testpassword, { force: true });
        cy.get('[data-cy="register-relation-fld"] select').select(testrelation);
        cy.get('[data-cy="register-terms-btn"]').click();
        cy.wait(500);

        cy.get('[data-cy="register-terms-popupclose-lnk"]').click();
        cy.get('[data-cy="register-terms-tgl"] input[type="checkbox"]').check({ force: true });
        cy.get('[data-cy="register-faceid-tgl"] input[type="checkbox"]').check({ force: true });
        cy.wait(1000);

        // TODO: Create account delete in prefs test first before we enable this!
        // cy.get('[data-cy="register-signup-btn"]').click();
    });
});
