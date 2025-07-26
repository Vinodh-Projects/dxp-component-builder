package com.adobe.aem.guides.wknd.core.models;

import javax.annotation.PostConstruct;
import java.util.List;
import java.util.ArrayList;
import org.apache.sling.api.resource.Resource;
import org.apache.sling.models.annotations.Model;
import org.apache.sling.models.annotations.Default;
import org.apache.sling.models.annotations.Optional;
import org.apache.sling.models.annotations.injectorspecific.ValueMapValue;

/**
 * TeaserBlockModel is a Sling Model for the Teaser Block component.
 */
@Model(adaptables = Resource.class, resourceType = "wknd/components/wkndai/teaser-block")
public class TeaserBlockModel {

    @ValueMapValue
    @Optional
    @Default(values = "Image Left / Text Right")
    private String layoutSelection;

    @ValueMapValue
    @Optional
    private String image;

    @ValueMapValue
    @Optional
    @Default(values = "")
    private String altText;

    @ValueMapValue
    @Optional
    @Default(values = "")
    private String title;

    @ValueMapValue
    @Optional
    @Default(values = "")
    private String description;

    @ValueMapValue
    @Optional
    private String ctaText;

    @ValueMapValue
    @Optional
    private String ctaLink;

    @ValueMapValue
    @Optional
    @Default(values = "_self")
    private String ctaTarget;

    @ValueMapValue
    @Optional
    @Default(values = "Vertical Center")
    private String alignment;

    @ValueMapValue
    @Optional
    private String backgroundColor;

    public String getLayoutSelection() {
        return layoutSelection;
    }

    public String getImage() {
        return image;
    }

    public String getAltText() {
        return altText;
    }

    public String getTitle() {
        return title;
    }

    public String getDescription() {
        return description;
    }

    public String getCtaText() {
        return ctaText;
    }

    public String getCtaLink() {
        return ctaLink;
    }

    public String getCtaTarget() {
        return ctaTarget;
    }

    public String getAlignment() {
        return alignment;
    }

    public String getBackgroundColor() {
        return backgroundColor;
    }
}