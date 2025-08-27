# Modern AdSense Setup Guide (2025)

This guide explains how to implement Google AdSense with Auto Ads in your AI News site.

## 1. AdSense Account Setup

1. Visit [Google AdSense](https://www.google.com/adsense)
2. Click "Get Started" or "Sign up now"
3. Enter your website URL and contact information
4. Complete site verification steps
5. Submit for review
6. Wait for approval (typically 1-3 weeks)

## 2. Enable Auto Ads

1. After approval, log in to AdSense
2. Navigate to "Sites" > Your Site
3. Click "Get Code"
4. You'll receive the AdSense code with your publisher ID
5. Add this code to your site's `<head>` section

## 3. Configure ads.yml

1. Open `_config/ads.yml`
2. Update your publisher ID from the AdSense code
3. Configure format preferences:
   ```yaml
   formats:
     in_page: true     # Standard display ads
     in_feed: true     # Ads between content items
     in_article: true  # Within article content
     matched: true     # Related content ads
     anchor: false     # Sticky ads
     vignette: false   # Full-screen ads
   ```

## 4. Layout Settings

Fine-tune your ad display in `ads.yml`:
```yaml
layout:
  ad_density: "medium"     # low, medium, high
  overlay_ads: false       # Floating/overlay ads
  anchor_position: "bottom" # For anchor ads
```

## 5. Testing & Optimization

1. Preview your site on multiple devices
2. Check ad placements and density
3. Monitor performance metrics in AdSense
4. Adjust settings based on:
   - Revenue
   - User experience
   - Page load times
   - Bounce rates

## 6. Best Practices

- Focus on high-quality, original content
- Maintain good user experience
- Follow AdSense program policies
- Don't exceed recommended ad density
- Regularly review performance
- Test different format combinations

Note: Modern AdSense primarily uses AI-driven Auto Ads for optimal placement and revenue. Manual ad units are being phased out in favor of this smart placement system.
   - Display ads
   - In-article ads
   - Feed ads
   - Matched content

The modern AdSense focuses on automatic placement optimization, but you can control:
- Ad density
- Ad types shown
- Placement preferences
- Page-level ad settings

## 4. Ad Unit Types and Recommended Sizes

### Sidebar Ads
- Size: 300x250, 300x600
- Best for: Desktop sidebar placement
- Type: Display ad

### In-Article Ads
- Size: Fluid
- Best for: Between paragraphs
- Type: In-article ad

### Before/After Content
- Size: 728x90, 970x90
- Best for: Top and bottom of content
- Type: Display ad

### Floating Ads
- Size: 300x250
- Best for: Fixed position on screen
- Type: Display ad

### Native Ads
- Size: Fluid
- Best for: Natural content integration
- Type: Native ad

### Matched Content
- Size: Fluid
- Best for: Content recommendations
- Type: Matched content

## 5. AdSense Policies

Remember to follow AdSense policies:
1. Don't place more than 3 ad units on mobile pages
2. Maintain good content-to-ad ratio
3. Don't click on your own ads
4. Don't use language that encourages clicking ads
5. Keep content family-friendly
6. Don't place ads near navigation elements

## 6. Testing Your Ads

1. Add your Publisher ID and Ad Unit IDs to `_config/ads.yml`
2. Run the test pipeline to verify ad placement
3. Check your site in both desktop and mobile views
4. Use Chrome Developer Tools to ensure ads load properly
5. Monitor AdSense dashboard for performance

## 7. Optimization Tips

1. Use a mix of ad formats for best results
2. Enable auto ads for optimal placement
3. Test different ad positions using A/B testing
4. Monitor CTR (Click-Through Rate) in AdSense dashboard
5. Use responsive ad units when possible
6. Don't overcrowd your content with ads

## 8. Troubleshooting

If ads aren't showing:
1. Verify your AdSense account is approved
2. Check that your ads.yml configuration is correct
3. Look for JavaScript errors in browser console
4. Ensure ad blockers are disabled for testing
5. Wait 24-48 hours for new ad units to start displaying

## 9. Mobile Optimization

1. Use responsive ad units
2. Limit the number of ads on mobile
3. Disable floating ads on small screens
4. Ensure ads don't interfere with content reading
