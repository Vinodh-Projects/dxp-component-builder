package com.adobe.aem.guides.wknd.core.models;

import org.apache.sling.api.resource.Resource;
import org.apache.sling.models.annotations.Model;
import org.apache.sling.models.annotations.injectorspecific.ValueMapValue;
import org.apache.sling.models.annotations.Optional;
import java.util.List;
import java.util.ArrayList;

/**
 * Sling Model for Hero Banner Component
 */
@Model(adaptables = Resource.class, resourceType = "wknd/components/wkndai/hero-banner")
public class HeroBannerModel {

    @ValueMapValue
    @Optional
    private String backgroundImage;

    @ValueMapValue
    @Optional
    private String headline;

    @ValueMapValue
    @Optional
    private String subheadline;

    @ValueMapValue
    @Optional
    private List<String> ctaButtons;

    @ValueMapValue
    @Optional
    private String alignment;

    @ValueMapValue
    @Optional
    private String overlay;

    public String getBackgroundImage() {
        return backgroundImage;
    }

    public String getHeadline() {
        return headline;
    }

    public String getSubheadline() {
        return subheadline;
    }

    public List<String> getCtaButtons() {
        return ctaButtons != null ? ctaButtons : new ArrayList<>();
    }

    public String getAlignment() {
        return alignment;
    }

    public String getOverlay() {
        return overlay;
    }
}