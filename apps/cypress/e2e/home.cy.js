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

// Test 1: Guided Tour
describe('Home Page & Guided Tour', () => {
    it('shows the guided tour dialog on first visit', () => {
        cy.visit('/');
        cy.containsAny('.slide-content', ['Willkommen', 'Welcome']);
        cy.wait(500);
        cy.get('.custom-dialog').should('be.visible');
        cy.wait(500);
        cy.get('.button-right').click();
        cy.wait(500);
        cy.get('.swiper-slide-active').should('contain', 'Plane Deine Trips');
        cy.wait(500);
        cy.get('.button-left').click();
        cy.get('.custom-dialog').should('not.be.visible');
        cy.wait(500);
    });
    it('does not show the guided tour dialog after it has been closed', () => {
        cy.visit('/');
        cy.wait(500);
        cy.get('.custom-dialog').should('be.visible');
        cy.wait(500);
        cy.get('.button-left').click();
        cy.wait(500);
        cy.reload();
        cy.wait(500);
        cy.get('.custom-dialog').should('not.be.visible');
        cy.wait(500);
    });
});

// Test 3: Button and link clicks
describe('Button and link clicks', () => {
    it('should navigate to trip planning after the trip panning button was clicked', () => {
        cy.visit('/');
        cy.wait(500);
        cy.get('.custom-dialog').should('be.visible');
        cy.wait(500);
        cy.get('.button-left').click();
        cy.wait(500);
        cy.get('.custom-dialog').should('not.be.visible');
        cy.wait(500);
        cy.get('.button.button-fill.button-large[href="/planning"]').click({ force: true });
        cy.wait(500);
        cy.containsAny('.title-large-text', ['Trip Planen', 'Trip Planning']);
        cy.wait(500);
    });
    it('should switch to the next news page 2', () => {
        cy.visit('/');
        cy.wait(500);
        cy.get('.custom-dialog').should('be.visible');
        cy.wait(500);
        cy.get('.button-left').click();
        cy.wait(500);
        cy.get('.custom-dialog').should('not.be.visible');
        cy.wait(500);
        cy.get('.segmented.segmented-round a').eq(1).click({ force: true });
        cy.wait(500);
        cy.containsAny('[data-cy="news-category-title"]', ['Campus News', 'Campus News']);
        cy.wait(500);
    });
    it('should switch to the next news page 3', () => {
        cy.visit('/');
        cy.wait(500);
        cy.get('.custom-dialog').should('be.visible');
        cy.wait(500);
        cy.get('.button-left').click();
        cy.wait(500);
        cy.get('.custom-dialog').should('not.be.visible');
        cy.wait(500);
        cy.get('.segmented.segmented-round a').eq(2).click({ force: true });
        cy.wait(500);
        cy.containsAny('[data-cy="news-category-title"]', ['Events', 'Events']);
        cy.wait(500);
    });
    it('should switch to the next news page 4', () => {
        cy.visit('/');
        cy.wait(500);
        cy.get('.custom-dialog').should('be.visible');
        cy.wait(500);
        cy.get('.button-left').click();
        cy.wait(500);
        cy.get('.custom-dialog').should('not.be.visible');
        cy.wait(500);
        cy.get('.segmented.segmented-round a').eq(3).click({ force: true });
        cy.wait(500);
        cy.containsAny('[data-cy="news-category-title"]', ['ICL Mobile News', 'ICL Mobile News']);
        cy.wait(500);
    });
    it('should switch to the next news page 1', () => {
        cy.visit('/');
        cy.wait(500);
        cy.get('.custom-dialog').should('be.visible');
        cy.wait(500);
        cy.get('.button-left').click();
        cy.wait(500);
        cy.get('.custom-dialog').should('not.be.visible');
        cy.wait(500);
        cy.get('.segmented.segmented-round a').eq(0).click({ force: true });
        cy.wait(500);
        cy.containsAny('[data-cy="news-category-title"]', ['Food & Drinks', 'Food & Drinks']);
        cy.wait(500);
    });
    it('should locate a button at the end of the page', () => {
        cy.visit('/');
        cy.wait(500);
        cy.get('.custom-dialog').should('be.visible');
        cy.wait(500);
        cy.get('.button-left').click();
        cy.wait(500);
        cy.get('.custom-dialog').should('not.be.visible');
        cy.wait(500);
        cy.get('.button.button-fill.button-large[href="#"]').scrollIntoView().should('be.visible');
        cy.wait(500);
    });
    it('should navigate to the preferences page when the gear link is clicked', () => {
        cy.visit('/');
        cy.get('.fa-gear').click();
        cy.wait(500);
        cy.containsAny('.title-large-text', ['Einstellungen', 'Preferences']);
        cy.wait(500);
    });
});

// Test 4: News list
describe('News clicks', () => {
    it('should open a sheet with news after list item was clicked', () => {
        cy.visit('/');
        cy.wait(500);
        cy.get('.custom-dialog').should('be.visible');
        cy.wait(500);
        cy.get('.button-left').click();
        cy.wait(500);
        cy.get('.custom-dialog').should('not.be.visible');
        cy.wait(500);
        cy.get('.segmented.segmented-round a').eq(1).click({ force: true });
        cy.wait(500);
        cy.get('.list.list-strong.media-list li').first().click();
        cy.wait(500);
        cy.get('.sheet-modal.sheet-modal-bottom.sheet-modal-push.iclNewsSheet.modal-in').should('be.visible');
        cy.wait(500);
        cy.get('.sheet-backdrop.backdrop-in').click({ force: true });
    });
});

describe('Open wallet after login', () => {
    beforeEach(() => {
        cy.login();
    });
    it('should navigate to the wallet page when the leaf link is clicked', () => {
        cy.visit('/');
        cy.wait(500);
        cy.get('.custom-dialog').should('be.visible');
        cy.wait(500);
        cy.get('.button-left').click();
        cy.wait(500);
        cy.get('.custom-dialog').should('not.be.visible');
        cy.wait(500);
        cy.get('.fa-leaf').click();
        cy.wait(500);
        cy.containsAny('.title-large-text', ['CO2 Wallet', 'CO2 Wallet']);
        cy.wait(500);
    });
});