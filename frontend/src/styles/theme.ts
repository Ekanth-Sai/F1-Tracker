import { createTheme } from '@mui/material/styles';

const theme = createTheme({
    palette: {
        mode: "dark",
        background: {
            default: "#0B0F1A",
            paper: "#141B2D",
        },
        primary: {
            main: "#E10600",
        },
        secondary: {
            main: "#00D1FF",
        },
    },
    shape: {
        borderRadius: 12,
    },
    typography: {
        fontFamily: "Roboto, sans-serif",
        h1: {
            fontFamily: "Montserrat, sans-serif",
            fontSize: "22px",
            fontWeight: 700,
        },
    },
});

export default theme;