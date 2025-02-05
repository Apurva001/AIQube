import { test } from '@playwright/test'
import LoginPage from './loginPage'
import fs from 'fs'

const testData = JSON.parse(fs.readFileSync(`./data/users.json`, `utf-8`))

test.describe('Login Page Tests', () => {
  let loginPage

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page)
  })
})
