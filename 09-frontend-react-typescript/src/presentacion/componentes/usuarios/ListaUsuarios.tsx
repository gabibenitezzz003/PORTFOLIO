import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  Avatar,
  IconButton,
  Menu,
  MenuItem,
  TextField,
  Select,
  FormControl,
  InputLabel,
  Grid,
  Paper,
  Skeleton,
  Alert,
  Snackbar
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Person as PersonIcon,
  Search as SearchIcon,
  FilterList as FilterListIcon
} from '@mui/icons-material';
import { Usuario, RolUsuario, EstadoUsuario } from '../../../dominio/entidades/Usuario';
import { CasoUsoGestionarUsuarios } from '../../../aplicacion/casosUso/CasoUsoGestionarUsuarios';
import { useUsuarios } from '../../../aplicacion/hooks/useUsuarios';
import { useNotificaciones } from '../../../aplicacion/hooks/useNotificaciones';

/**
 * Props del componente ListaUsuarios
 */
interface ListaUsuariosProps {
  casoUsoGestionarUsuarios: CasoUsoGestionarUsuarios;
  onEditarUsuario: (usuario: Usuario) => void;
  onEliminarUsuario: (usuario: Usuario) => void;
  onVerDetalles: (usuario: Usuario) => void;
}

/**
 * Filtros de búsqueda
 */
interface FiltrosUsuarios {
  busqueda: string;
  rol: RolUsuario | '';
  estado: EstadoUsuario | '';
}

/**
 * Componente para mostrar la lista de usuarios
 * 
 * @author Gabriel - Arquitecto de Software
 */
export const ListaUsuarios: React.FC<ListaUsuariosProps> = ({
  casoUsoGestionarUsuarios,
  onEditarUsuario,
  onEliminarUsuario,
  onVerDetalles
}) => {
  // Estados
  const [filtros, setFiltros] = useState<FiltrosUsuarios>({
    busqueda: '',
    rol: '',
    estado: ''
  });
  const [pagina, setPagina] = useState(0);
  const [limite, setLimite] = useState(10);
  const [ordenarPor, setOrdenarPor] = useState('fechaCreacion');
  const [orden, setOrden] = useState<'asc' | 'desc'>('desc');
  const [menuAbierto, setMenuAbierto] = useState<{ anchorEl: HTMLElement | null; usuario: Usuario | null }>({
    anchorEl: null,
    usuario: null
  });

  // Hooks personalizados
  const { usuarios, paginacion, cargando, error, cargarUsuarios } = useUsuarios(casoUsoGestionarUsuarios);
  const { mostrarNotificacion } = useNotificaciones();

  // Cargar usuarios al montar el componente
  useEffect(() => {
    cargarUsuarios({
      ...filtros,
      pagina: pagina + 1,
      limite,
      ordenarPor,
      orden
    });
  }, [filtros, pagina, limite, ordenarPor, orden]);

  // Manejar cambio de página
  const manejarCambioPagina = (event: unknown, nuevaPagina: number) => {
    setPagina(nuevaPagina);
  };

  // Manejar cambio de límite
  const manejarCambioLimite = (event: React.ChangeEvent<HTMLInputElement>) => {
    setLimite(parseInt(event.target.value, 10));
    setPagina(0);
  };

  // Manejar cambio de filtros
  const manejarCambioFiltros = (nuevosFiltros: Partial<FiltrosUsuarios>) => {
    setFiltros(prev => ({ ...prev, ...nuevosFiltros }));
    setPagina(0);
  };

  // Manejar apertura del menú
  const manejarAbrirMenu = (event: React.MouseEvent<HTMLElement>, usuario: Usuario) => {
    setMenuAbierto({
      anchorEl: event.currentTarget,
      usuario
    });
  };

  // Manejar cierre del menú
  const manejarCerrarMenu = () => {
    setMenuAbierto({
      anchorEl: null,
      usuario: null
    });
  };

  // Manejar acciones del menú
  const manejarAccionMenu = (accion: string) => {
    const usuario = menuAbierto.usuario;
    if (!usuario) return;

    switch (accion) {
      case 'editar':
        onEditarUsuario(usuario);
        break;
      case 'eliminar':
        onEliminarUsuario(usuario);
        break;
      case 'ver':
        onVerDetalles(usuario);
        break;
    }

    manejarCerrarMenu();
  };

  // Obtener color del chip de estado
  const obtenerColorEstado = (estado: EstadoUsuario): 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' => {
    switch (estado) {
      case EstadoUsuario.ACTIVO:
        return 'success';
      case EstadoUsuario.INACTIVO:
        return 'default';
      case EstadoUsuario.SUSPENDIDO:
        return 'error';
      case EstadoUsuario.PENDIENTE_VERIFICACION:
        return 'warning';
      default:
        return 'default';
    }
  };

  // Obtener color del chip de rol
  const obtenerColorRol = (rol: RolUsuario): 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' => {
    switch (rol) {
      case RolUsuario.ADMINISTRADOR:
        return 'error';
      case RolUsuario.MODERADOR:
        return 'warning';
      case RolUsuario.USUARIO:
        return 'primary';
      case RolUsuario.INVITADO:
        return 'default';
      default:
        return 'default';
    }
  };

  // Renderizar skeleton mientras carga
  if (cargando && usuarios.length === 0) {
    return (
      <Box>
        <Grid container spacing={3}>
          {Array.from({ length: 5 }).map((_, index) => (
            <Grid item xs={12} key={index}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={2}>
                    <Skeleton variant="circular" width={40} height={40} />
                    <Box flexGrow={1}>
                      <Skeleton variant="text" width="60%" />
                      <Skeleton variant="text" width="40%" />
                    </Box>
                    <Skeleton variant="rectangular" width={100} height={32} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  return (
    <Box>
      {/* Filtros */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Buscar usuarios"
              value={filtros.busqueda}
              onChange={(e) => manejarCambioFiltros({ busqueda: e.target.value })}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Rol</InputLabel>
              <Select
                value={filtros.rol}
                onChange={(e) => manejarCambioFiltros({ rol: e.target.value as RolUsuario | '' })}
                label="Rol"
              >
                <MenuItem value="">Todos</MenuItem>
                <MenuItem value={RolUsuario.ADMINISTRADOR}>Administrador</MenuItem>
                <MenuItem value={RolUsuario.MODERADOR}>Moderador</MenuItem>
                <MenuItem value={RolUsuario.USUARIO}>Usuario</MenuItem>
                <MenuItem value={RolUsuario.INVITADO}>Invitado</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Estado</InputLabel>
              <Select
                value={filtros.estado}
                onChange={(e) => manejarCambioFiltros({ estado: e.target.value as EstadoUsuario | '' })}
                label="Estado"
              >
                <MenuItem value="">Todos</MenuItem>
                <MenuItem value={EstadoUsuario.ACTIVO}>Activo</MenuItem>
                <MenuItem value={EstadoUsuario.INACTIVO}>Inactivo</MenuItem>
                <MenuItem value={EstadoUsuario.SUSPENDIDO}>Suspendido</MenuItem>
                <MenuItem value={EstadoUsuario.PENDIENTE_VERIFICACION}>Pendiente Verificación</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Box display="flex" justifyContent="flex-end">
              <IconButton>
                <FilterListIcon />
              </IconButton>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Tabla de usuarios */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Usuario</TableCell>
                <TableCell>Rol</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Último Acceso</TableCell>
                <TableCell align="right">Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {usuarios.map((usuario) => (
                <TableRow key={usuario.id} hover>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={2}>
                      <Avatar
                        src={usuario.avatar}
                        alt={usuario.obtenerNombreCompleto()}
                        sx={{ width: 40, height: 40 }}
                      >
                        {usuario.obtenerIniciales()}
                      </Avatar>
                      <Box>
                        <Typography variant="subtitle2">
                          {usuario.obtenerNombreCompleto()}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {usuario.correoElectronico}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={usuario.rol}
                      color={obtenerColorRol(usuario.rol)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={usuario.estado}
                      color={obtenerColorEstado(usuario.estado)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {usuario.ultimoAcceso
                      ? new Date(usuario.ultimoAcceso).toLocaleDateString()
                      : 'Nunca'
                    }
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      onClick={(e) => manejarAbrirMenu(e, usuario)}
                      size="small"
                    >
                      <MoreVertIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Paginación */}
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={paginacion.total}
          rowsPerPage={limite}
          page={pagina}
          onPageChange={manejarCambioPagina}
          onRowsPerPageChange={manejarCambioLimite}
          labelRowsPerPage="Filas por página:"
          labelDisplayedRows={({ from, to, count }) =>
            `${from}-${to} de ${count !== -1 ? count : `más de ${to}`}`
          }
        />
      </Card>

      {/* Menú de acciones */}
      <Menu
        anchorEl={menuAbierto.anchorEl}
        open={Boolean(menuAbierto.anchorEl)}
        onClose={manejarCerrarMenu}
      >
        <MenuItem onClick={() => manejarAccionMenu('ver')}>
          <PersonIcon sx={{ mr: 1 }} />
          Ver Detalles
        </MenuItem>
        <MenuItem onClick={() => manejarAccionMenu('editar')}>
          <EditIcon sx={{ mr: 1 }} />
          Editar
        </MenuItem>
        <MenuItem onClick={() => manejarAccionMenu('eliminar')} sx={{ color: 'error.main' }}>
          <DeleteIcon sx={{ mr: 1 }} />
          Eliminar
        </MenuItem>
      </Menu>

      {/* Snackbar para errores */}
      <Snackbar
        open={Boolean(error)}
        autoHideDuration={6000}
        onClose={() => {}}
      >
        <Alert severity="error" onClose={() => {}}>
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
};
