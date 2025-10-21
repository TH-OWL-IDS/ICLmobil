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
const username = 'sascha@hangar-18.com';
const testUser = 'test@example.com';
const password = 'test1234';

// Custom commands
Cypress.Commands.add('containsAny', (selector, texts) => {
    cy.get(selector).then($el => {
        const found = texts.some(t => $el.text().includes(t));
        expect(found, `One of [${texts.join(', ')}] is present`).to.be.true;
    });
});

// Test 1: Account login page loads
describe('Login page loads', () => {
    it('should display the login page', () => {
        cy.visit('/login');
        cy.containsAny('.title-large-text', ['Anmelden', 'Login']);
    });
});

// Test 2: Account login fields
describe('Login Input Fields', () => {
    it('check if we have username and password fields on login page', () => {
        cy.visit('/login');
        cy.get('[data-cy="login-email-fld"] input').should('be.visible');
        cy.get('[data-cy="login-password-fld"] input').should('be.visible');
        cy.wait(500);
    });
});

// Test 3: Password recovery
// TODO: Test complete recover flow with working email if possible
describe('Password recovery', () => {
    it('open password recovery dialog and enter email, click send and wait for response', () => {
        cy.visit('/login');
        cy.get('[data-cy="login-pwd-recover-lnk"]').click();
        cy.get('.dialog input[type="text"]').type(testUser);
        cy.wait(500);
        cy.get('.dialog .dialog-button-strong').click();
        cy.wait(1000);
        cy.get('.dialog .dialog-button-strong').click();
    });
});

// Test 4: Register
describe('Register Account', () => {
    it('open account registration page', () => {
        cy.visit('/login');
        cy.get('[data-cy="login-register-lnk"]').click();
        cy.wait(1000);
    });
});

// Test 5: Account login
describe('Login Test', () => {
    it('enter data for test user, toggle faceID and login', () => {
        cy.visit('/login');
        cy.get('[data-cy="login-email-fld"] input').type(username);
        cy.get('[data-cy="login-password-fld"] input').type(password);
        cy.get('[data-cy="login-faceid-tgl"] input[type="checkbox"]').check({ force: true });
        cy.wait(1000);
        cy.get('[data-cy="login-login-btn"]').click();
    });
});
