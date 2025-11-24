# Code Signing & Notarization Instructions

This guide explains how to sign and notarize the Easy AALM Mac app so it can be distributed without security warnings.

## Prerequisites

1. **Apple Developer Account** ($99/year)
2. **Xcode** installed on a Mac
3. **Developer ID Application certificate** in Keychain
   - Get this from [Apple Developer Certificates](https://developer.apple.com/account/resources/certificates/list)
   - Download and install the certificate
4. **App-specific password** for notarization
   - Create at [appleid.apple.com](https://appleid.apple.com) → Security → App-Specific Passwords

## Quick Start (Automated)

On your Mac, run:

```bash
cd /path/to/aalm-app
./sign-and-notarize.sh
```

The script will guide you through the entire process.

## Manual Process

If you prefer to do it step-by-step:

### 1. Find Your Signing Identity

```bash
security find-identity -v -p codesigning
```

Look for something like: `Developer ID Application: Your Name (TEAM_ID)`

### 2. Sign the App

```bash
# Remove extended attributes
xattr -cr "Easy AALM.app"

# Sign
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name (TEAM_ID)" \
  "Easy AALM.app"

# Verify
codesign --verify --deep --strict --verbose=2 "Easy AALM.app"
spctl -a -t exec -vv "Easy AALM.app"
```

### 3. Create Zip for Notarization

```bash
ditto -c -k --keepParent "Easy AALM.app" "Easy-AALM.zip"
```

### 4. Submit for Notarization

```bash
xcrun notarytool submit "Easy-AALM.zip" \
  --apple-id "your@email.com" \
  --password "your-app-specific-password" \
  --team-id "TEAM_ID" \
  --wait
```

This will take 5-30 minutes. You'll see either success or failure.

### 5. Staple the Notarization Ticket

Once approved:

```bash
xcrun stapler staple "Easy AALM.app"
```

### 6. Verify

```bash
spctl -a -t exec -vv "Easy AALM.app"
```

Should show: `Easy AALM.app: accepted`

## Troubleshooting

### "No identity found"

Make sure you've:
1. Enrolled in Apple Developer Program
2. Created a Developer ID Application certificate at developer.apple.com
3. Downloaded and double-clicked the certificate to install it in Keychain

### "Notarization failed"

Get detailed logs:
```bash
# Get submission ID from the notarytool output
xcrun notarytool log <SUBMISSION_ID> \
  --apple-id "your@email.com" \
  --password "your-app-specific-password" \
  --team-id "TEAM_ID"
```

Common issues:
- Unsigned frameworks or libraries
- Invalid Info.plist
- Missing entitlements

### "Invalid password"

You need an **app-specific password**, not your regular Apple ID password:
1. Go to appleid.apple.com
2. Sign in
3. Security → App-Specific Passwords
4. Generate New Password
5. Copy it (you can't view it again)

## After Notarization

Once complete:

1. **Test locally** - Double-click the app, should open without warnings
2. **Commit to Git** - The signed app can be committed
3. **Update README** - Remove the "right-click → Open" warning

## Automation

For CI/CD, you can store credentials securely:

```bash
# Store credentials in keychain
xcrun notarytool store-credentials "notarization-profile" \
  --apple-id "your@email.com" \
  --password "your-app-specific-password" \
  --team-id "TEAM_ID"

# Then use the profile
xcrun notarytool submit "Easy-AALM.zip" \
  --keychain-profile "notarization-profile" \
  --wait
```

## Resources

- [Apple Code Signing Guide](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/)
- [Notarization Documentation](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [notarytool User Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution/customizing_the_notarization_workflow)
