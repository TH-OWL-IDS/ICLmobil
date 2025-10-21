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

const username = 'your_username@example.com';
const password = '12345678';

Cypress.Commands.add('containsAny', (selector, texts) => {
    const normalize = s => s.replace(/\s+/g, ' ').trim();
    cy.get(selector).then($el => {
        const text = normalize($el.text());
        const found = texts.some(t => text.includes(normalize(t)));
        expect(found, `One of [${texts.join(', ')}] is present in: "${$el.text()}"`).to.be.true;
    });
});

Cypress.Commands.add('containsAnyAfter', { prevSubject: 'element' }, (subject, texts) => {
    const text = subject.text();
    const normalizedText = text.replace(/\s+/g, ' ').trim();
    const found = texts.some(t => normalizedText.includes(t));
    expect(found, `One of [${texts.join(', ')}] is present in: "${text}"`).to.be.true;
});

Cypress.Commands.add('login', () => {
    cy.visit('/login');
    cy.get('[data-cy="login-email-fld"] input').type(username);
    cy.get('[data-cy="login-password-fld"] input').type(password);
    cy.get('[data-cy="login-faceid-tgl"] input[type="checkbox"]').check({ force: true });
    cy.get('[data-cy="login-login-btn"]').click();
    cy.wait(1000);
});