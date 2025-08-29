export class CategoryImageManager {
    static categories = [
        'technology', 'business', 'science', 
        'health', 'sports', 'entertainment', 
        'general'
    ];

    static async createPlaceholderImage(text, bgColor = '#e41e31') {
        const canvas = document.createElement('canvas');
        canvas.width = 600;
        canvas.height = 400;
        
        const ctx = canvas.getContext('2d');
        
        // Background
        ctx.fillStyle = bgColor;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Text
        ctx.fillStyle = 'white';
        ctx.font = 'bold 48px var(--font-primary, sans-serif)';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text.toUpperCase(), canvas.width / 2, canvas.height / 2);
        
        return new Promise((resolve) => {
            canvas.toBlob((blob) => {
                const url = URL.createObjectURL(blob);
                resolve(url);
            }, 'image/jpeg', 0.9);
        });
    }

    static async generateCategoryImages() {
        for (const category of this.categories) {
            const imageUrl = await this.createPlaceholderImage(category);
            const response = await fetch(imageUrl);
            const blob = await response.blob();
            
            const formData = new FormData();
            formData.append('image', blob, `${category}.jpg`);
            
            try {
                await fetch(`/api/upload-category-image`, {
                    method: 'POST',
                    body: formData
                });
            } catch (error) {
                console.warn(`Failed to upload category image for ${category}`);
            }
        }
    }
}
