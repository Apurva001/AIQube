/* Scenario 1: 
Login as a standard user to verify the products page and logout from the application

Scenario Description: 
User logs into the website and verifies all the elements on the products page and logs out from the application. 
This is like a Smoke test.

Test test.steps:
1.	User is on the Login Page
2.	Verify the Logo, title, url, username, password fields, login button, login and password credentials on the login page
3.	Login as a standard user
4.	User is on the Landing/Products page. Verify the Landing page logo and URL
5.	Verify the PRODUCTS title and peek image visible on the home page
6.	Verify all the options Burger menu item, ALL ITEMS; ABOUT; LOGOUT AND RESET APP STATE are visible on inventory sidebar links on left side of the page
7.	Verify the shopping cart icon and product sort container visible on the top right of the page
8.	Verify the Inventory Product item list is visible
9.	Select the Product sort container as “Price (low to high)” and verify the inventory item list is displayed correctly in the right order selected.
10.	Verify the footer text and swag bot footer is visible
11.	Click on “About” navbar link from the “inventory sidebar panel” and check whether user is navigated to saucelabs page
12.	Verify the Twitter, Facebook, Linkedin logo visible 
13.	Click on Twitter social link and verify user is navigated to Twitter page
14.	Click on Facebook social link and verify user is navigated to Facebook page
15.	Click on LinkedIn social link and verify user is navigated to LinkedIn page
16.	User logout from the application and verify the login page
*/

import test from '../testFixtures/fixture'
import { expect } from '@playwright/test'
import fs from 'fs'
import { username, password, loginButton } from '../pageobjects/loginPage'
import {
	twitterLink,
	facebookLink,
	linkedInLink
} from '../pageobjects/productsPage'
const testData = JSON.parse(fs.readFileSync(`./data/users.json`, `utf-8`))

import {
	baseUrl,
	title,
	landingPageUrl,
	sauceLabsTitle,
	sauceLabsUrl,
	onesie,
	fleeceJacket,
	twitterTitle,
	twitterUrl,
	facebookTitle,
	facebookUrl,
	linkedInTitle,
	linkedInUrl
} from '../config'

test.describe.parallel(
	'@smoke: Login as a standard user to verify the products page and logout from the application',
	() => {
		test('Login to App as a standard user', async ({
			loginPage,
			productsPage
		}) => {
			await test.step(`Open the APP and check logo`, async () => {
				await loginPage.openApp()
				await loginPage.loginPageLogo()
				expect(await loginPage.getTitle()).toBe(title)
				expect(await loginPage.getUrl()).toContain(baseUrl)
			})
			
		
})
})
