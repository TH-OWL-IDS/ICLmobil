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

// Test 1: Check for wallet info
describe('Wallet page shows information', () => {
    beforeEach(() => {
        cy.login();
    });
    it('should display the wallet page and show all user stats and infos', () => {
        cy.visit('/wallet');
        cy.containsAny('.title-large-text', ['CO2 Wallet', 'CO2 Wallet']);
        cy.get('.page-content').eq(0).scrollTo('top');
        cy.get('.grid-cols-3 > :nth-child(1) > .button').containsAny('.button', ['Fahrten', 'Rides']);
        cy.get('.page-content').eq(0).scrollTo('top');
        cy.get('.grid-cols-1 > :nth-child(1) > .button')
        .containsAnyAfter(['Gesch. CO2 Einsparung', 'Estimated CO2 Savings']);
        cy.get(':nth-child(5) > .button')
        .containsAnyAfter(['Experience Score', 'Erfahrung']);
        cy.get(':nth-child(5) > .button')
        .containsAnyAfter(['Points', 'Punkte']);
        cy.get(':nth-child(5) > .button')
        .containsAnyAfter(['Ranking', 'Platz']);
        cy.get(':nth-child(6) > .button')
        .containsAnyAfter(['Usage statistics', 'Nutzungs Statistik']);
        cy.get(':nth-child(7) > .button')
        .containsAnyAfter(['Top 5 Ranking', 'Bestenliste']);
    });
});
