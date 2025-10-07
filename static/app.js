window.addEventListener("load", (event) => {
  window.users = {
    _insertForm: $('#insert-form'),
    _insertName: $('#insert-name'),
    _updateForm: $('#update-form'),
    _updateName: $('#update-name'),
    _tableBody: $('#table-body'),
    
    // Render
    // ----------------------------------------------
    list: (list) => {
      users._insertForm.removeClass('hide');
      users._updateForm.addClass('hide');
      users._insertName.val('');
      users._tableBody.empty();
      users._tableBody.append(list.map((user) => {
        return '<tr><td>' + user.id + '</td><td>' + user.name + '</td><td><button onclick="users.get(' + user.id + ')">Görüntüle</button> <button onclick="users.delete(' + user.id + ')">Sil</button></td></tr>';
      }))
    },
    show: (user) => {
      users._insertForm.addClass('hide');
      users._updateForm.removeClass('hide');
      users._updateName.val(user.name);
      users._user = user;
    },

    // Data
    // ----------------------------------------------    
    fetch: () => {
      $.ajax({
        url: '/users',
      }).done((list) => {
        users.list(list);
      })
    },
    get: (id) => {
      $.ajax({
        url: '/users/'+id,
      }).done((user) => {
        users.show(user);
      })
    },
    insert: (id) => {
      $.ajax({
        url: '/users',
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        data: JSON.stringify({name: users._insertName.val()})
      }).done(() => {
        users.fetch();    
      })
    },
    delete: (id) => {
      $.ajax({
        url: '/users/'+id,
        type: 'DELETE'
      }).done(() => {
        users.fetch();    
      })
    },
    update: () => {
      users._user.name = users._updateName.val();
      $.ajax({
        url: '/users/'+users._user.id,
        type: 'PUT',
        contentType: 'application/json',
        dataType: 'json',
        data: JSON.stringify(users._user)
      }).done(() => {
        users.fetch(); 
      })
    }
  };

  return({
    init: () => {
      users.fetch();       
    },
  }).init();
});