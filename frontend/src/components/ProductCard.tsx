import {
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Chip,
  Link,
  Typography,
} from "@mui/material";
import type { Product } from "../utils/types";

export default function ProductCard({ product }: { product: Product }) {
  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "start",
            mb: 1,
          }}
        >
          <Typography variant="h6" component="div">
            {product.name}
          </Typography>
          {product.is_discounted && (
            <Chip label="On Sale" color="error" size="small" />
          )}
        </Box>
        {product.searched_term !== product.original_term && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Searched for: {product.original_term}
          </Typography>
        )}
        <Box sx={{ mt: 2 }}>
          <Typography
            variant="h6"
            color={product.is_discounted ? "error" : "primary"}
          >
            {product.price.toFixed(2)} zł
          </Typography>
        </Box>
      </CardContent>
      <CardActions>
        <Link
          href={product.url}
          target="_blank"
          rel="noopener noreferrer"
          underline="none"
        >
          <Button size="small" variant="outlined">
            View Product
          </Button>
        </Link>
      </CardActions>
    </Card>
  );
}
