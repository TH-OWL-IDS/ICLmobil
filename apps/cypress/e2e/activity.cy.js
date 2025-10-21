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

const testfeedback = 'Sadly, this is only cypress test feedback to test end to end user interactions with the frontend. Sorry :(';

// Test 1: Check for activities
describe('Activity page shows rides', () => {
    beforeEach(() => {
        cy.login();
    });
    it('should display the activity page and show user next, started and previous rides', () => {
        cy.visit('/activity');
        cy.wait(1000);
        cy.containsAny('.title-large-text', ['Your Activity', 'Deine Aktivität']);
        cy.get('.page-content').eq(0).scrollTo('top');

        // Check next rides (if any)
        cy.get('body').then($body => {
            if ($body.find('[data-cy="activity-nonextrides-btn"]').length) {
                cy.get('[data-cy="activity-nonextrides-btn"]').click({ force: true });
                cy.visit('/activity');
                cy.wait(1000);
            } else {
                cy.get('[data-cy="activity-nextrides-lst"]').scrollIntoView().should('be.visible');
                cy.get('[data-cy="activity-nextrides-lst"] > ul > li > a').first().click({ force: true });
                cy.wait(500);
                cy.get('.nextRide > .sheet-modal-inner > .page-content').eq(0).scrollTo('center');
                cy.get('[data-cy="nextride-startride-btn"]').click({ force: true });
                cy.wait(500);
                // cy.get('[data-cy="nextride-close-btn"]').click({ force: true });
                // cy.wait(500);
            }
        });

        // Check started rides (if any)
        cy.get('body').then($body => {
            if ($body.find('[data-cy="activity-startedrides-lst"]').length) {
                cy.get('[data-cy="activity-startedrides-lst"]').scrollIntoView().should('be.visible');
                cy.get('[data-cy="activity-startedrides-lst"] > ul > li > a').first().click({ force: true });
                cy.wait(500);
                cy.get('.startedRide > .sheet-modal-inner > .page-content').eq(0).scrollTo('center');
                cy.get('[data-cy="startedride-endride-btn"]').click({ force: true });
                cy.wait(500);
                cy.get('.dialog-button-strong').click();
                cy.wait(1000);
                // cy.get('.startedRide > .toolbar > .toolbar-inner > .right > .link > .icon').click({ force: true });
                // cy.wait(500);
            }
        });

        // Check previous rides (if any)
        cy.get('body').then($body => {
            if ($body.find('[data-cy="activity-nopreviousrides-btn"]').length) {
                cy.get('[data-cy="activity-nopreviousrides-btn"]').click({ force: true });
            } else {
                cy.get('[data-cy="activity-previousrides-lst"]').scrollIntoView().should('be.visible');
                cy.get('[data-cy="activity-previousrides-lst"] > ul > li > div > a').first().click({ force: true });
                cy.wait(500);
                cy.get('.previousRide > .sheet-modal-inner > .page-content').eq(0).scrollTo('bottom');
                cy.get('[data-cy="previousride-feedback-btn"]').click();
                cy.get('[data-cy="feedback-text-fld"] textarea').type(testfeedback, { force: true });
                cy.get('.feedback > .sheet-modal-inner > .page-content').eq(0).scrollTo('bottom');
                cy.get('[data-cy="feedback-thumbsup-btn"]').click();
                cy.wait(500);
                cy.get('[data-cy="feedback-thumbsdown-btn"]').click();
                cy.wait(500);
                cy.get('[data-cy="feedback-thumbsup-btn"]').click();
                cy.get('[data-cy="feedback-send-btn"]').click();
                cy.wait(1000);
                // cy.get('.previousRide > .toolbar > .toolbar-inner > .right > .link > .icon').click({ force: true });
                // cy.wait(500);
            }
        });
    });
});
