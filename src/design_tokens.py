# src/design_tokens.py
"""
Design Tokens - Sistema unificado de cores, tipografia e espaçamentos
para consistência visual em toda a aplicação IrrigoSystem Dashboard
"""

class DesignTokens:
    """Tokens de design centralizados para consistência visual"""
    
    # ========== CORES ==========
    COLORS = {
        # Cores principais
        "primary": "#5BAEDC",
        "primary_dark": "#4A9BC4", 
        "primary_light": "#7CC4E8",
        
        # Cores secundárias
        "secondary": "#34A853",
        "secondary_dark": "#2E8B47",
        "secondary_light": "#4FB366",
        
        # Cores de estado
        "success": "#34A853",
        "warning": "#FBBC04",
        "error": "#EA4335",
        "info": "#4285F4",
        
        # Cores neutras
        "neutral": {
            "50": "#F9FAFB",
            "100": "#F3F4F6",
            "200": "#E5E7EB", 
            "300": "#D1D5DB",
            "400": "#9CA3AF",
            "500": "#6B7280",
            "600": "#4B5563",
            "700": "#374151",
            "800": "#1F2937",
            "900": "#111827"
        },
        
        # Cores de fundo
        "background": {
            "primary": "#FFFFFF",
            "secondary": "#F7F7F7",
            "tertiary": "#F9FAFB"
        },
        
        # Cores de texto
        "text": {
            "primary": "#212529",
            "secondary": "#6B7280", 
            "tertiary": "#9CA3AF",
            "inverse": "#FFFFFF"
        }
    }
    
    # ========== TIPOGRAFIA ==========
    TYPOGRAPHY = {
        "font_families": {
            "primary": "Roboto, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            "heading": "Lora, Georgia, serif",
            "mono": "'JetBrains Mono', 'Fira Code', monospace"
        },
        
        "sizes": {
            "xs": "0.75rem",      # 12px
            "sm": "0.875rem",     # 14px  
            "base": "1rem",       # 16px
            "lg": "1.125rem",     # 18px
            "xl": "1.25rem",      # 20px
            "2xl": "1.5rem",      # 24px
            "3xl": "1.875rem",    # 30px
            "4xl": "2.25rem",     # 36px
            "5xl": "3rem"         # 48px
        },
        
        "weights": {
            "light": "300",
            "normal": "400", 
            "medium": "500",
            "semibold": "600",
            "bold": "700",
            "extrabold": "800"
        },
        
        "line_heights": {
            "tight": "1.25",
            "normal": "1.5", 
            "relaxed": "1.75"
        }
    }
    
    # ========== ESPAÇAMENTOS ==========
    SPACING = {
        "0": "0",
        "1": "0.25rem",    # 4px
        "2": "0.5rem",     # 8px  
        "3": "0.75rem",    # 12px
        "4": "1rem",       # 16px
        "5": "1.25rem",    # 20px
        "6": "1.5rem",     # 24px
        "8": "2rem",       # 32px
        "10": "2.5rem",    # 40px
        "12": "3rem",      # 48px
        "16": "4rem",      # 64px
        "20": "5rem",      # 80px
        "24": "6rem"       # 96px
    }
    
    # ========== SHADOWS ==========
    SHADOWS = {
        "none": "none",
        "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        "base": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
        "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
        "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
        "2xl": "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
        "inner": "inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)"
    }
    
    # ========== BORDER RADIUS ==========
    RADIUS = {
        "none": "0",
        "sm": "0.125rem",   # 2px
        "base": "0.25rem",  # 4px
        "md": "0.375rem",   # 6px
        "lg": "0.5rem",     # 8px
        "xl": "0.75rem",    # 12px
        "2xl": "1rem",      # 16px
        "3xl": "1.5rem",    # 24px
        "full": "9999px"
    }
    
    # ========== BREAKPOINTS ==========
    BREAKPOINTS = {
        "xs": "320px",
        "sm": "640px",
        "md": "768px",
        "lg": "1024px",
        "xl": "1280px",
        "2xl": "1536px"
    }
    
    # ========== ANIMATIONS ==========
    ANIMATIONS = {
        "duration": {
            "fast": "150ms",
            "normal": "300ms",
            "slow": "500ms"
        },
        "easing": {
            "linear": "linear",
            "ease_in": "ease-in",
            "ease_out": "ease-out", 
            "ease_in_out": "ease-in-out"
        }
    }
    
    @classmethod
    def get_css_variables(cls):
        """Gera CSS custom properties dos design tokens"""
        css_vars = []
        
        # Cores
        for key, value in cls.COLORS.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    css_vars.append(f"--color-{key}-{sub_key}: {sub_value};")
            else:
                css_vars.append(f"--color-{key}: {value};")
        
        # Espaçamentos
        for key, value in cls.SPACING.items():
            css_vars.append(f"--spacing-{key}: {value};")
            
        # Tipografia
        for key, value in cls.TYPOGRAPHY["sizes"].items():
            css_vars.append(f"--text-{key}: {value};")
            
        # Shadows
        for key, value in cls.SHADOWS.items():
            css_vars.append(f"--shadow-{key}: {value};")
            
        # Border radius  
        for key, value in cls.RADIUS.items():
            css_vars.append(f"--radius-{key}: {value};")
        
        return ":root {\n  " + "\n  ".join(css_vars) + "\n}"
    
    @classmethod
    def get_streamlit_theme(cls):
        """Retorna configuração de tema para Streamlit"""
        return {
            "primaryColor": cls.COLORS["primary"],
            "backgroundColor": cls.COLORS["background"]["primary"], 
            "secondaryBackgroundColor": cls.COLORS["background"]["secondary"],
            "textColor": cls.COLORS["text"]["primary"],
            "font": cls.TYPOGRAPHY["font_families"]["primary"]
        }


# ========== UTILITÁRIOS ==========

def get_color(color_path: str) -> str:
    """
    Recupera uma cor dos design tokens usando dot notation
    Ex: get_color("primary") -> "#5BAEDC"
    Ex: get_color("neutral.500") -> "#6B7280"
    """
    keys = color_path.split(".")
    value = DesignTokens.COLORS
    
    try:
        for key in keys:
            value = value[key]
        return value
    except KeyError:
        return DesignTokens.COLORS["neutral"]["500"]  # fallback


def get_spacing(size: str) -> str:
    """
    Recupera um valor de espaçamento
    Ex: get_spacing("4") -> "1rem"
    """
    return DesignTokens.SPACING.get(size, DesignTokens.SPACING["4"])


def get_shadow(size: str) -> str:
    """
    Recupera um valor de shadow
    Ex: get_shadow("md") -> "0 4px 6px -1px rgba(0, 0, 0, 0.1)..."
    """
    return DesignTokens.SHADOWS.get(size, DesignTokens.SHADOWS["base"])


def generate_button_styles() -> str:
    """Gera CSS para botões padronizados"""
    return f"""
    <style>
    .stButton > button {{
        font-family: {DesignTokens.TYPOGRAPHY["font_families"]["primary"]};
        font-weight: {DesignTokens.TYPOGRAPHY["weights"]["medium"]};
        border-radius: {DesignTokens.RADIUS["md"]};
        box-shadow: {DesignTokens.SHADOWS["sm"]};
        transition: all {DesignTokens.ANIMATIONS["duration"]["normal"]} {DesignTokens.ANIMATIONS["easing"]["ease_out"]};
    }}
    
    .stButton > button:hover {{
        box-shadow: {DesignTokens.SHADOWS["md"]};
        transform: translateY(-1px);
    }}
    
    .primary-button {{
        background-color: {DesignTokens.COLORS["primary"]} !important;
        color: {DesignTokens.COLORS["text"]["inverse"]} !important;
        border: none !important;
    }}
    
    .secondary-button {{
        background-color: transparent !important;
        color: {DesignTokens.COLORS["primary"]} !important;
        border: 1px solid {DesignTokens.COLORS["primary"]} !important;
    }}
    
    .danger-button {{
        background-color: {DesignTokens.COLORS["error"]} !important;
        color: {DesignTokens.COLORS["text"]["inverse"]} !important;
        border: none !important;
    }}
    </style>
    """